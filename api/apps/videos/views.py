import os
import time
import logging
import tempfile
import re
from django.core.cache import cache
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Videos, Highlight
from .serializers import VideosSerializer, HighlightSerializer
import google.generativeai as genai

# ロガーを設定
logger = logging.getLogger(__name__)

# Gemini APIの設定
genai.configure(api_key=settings.GEMINI_API_KEY)


class VideosView(APIView):
    def post(self, request):
        video_id = request.data.get('video_id')
        channel_id = request.data.get('channel_id')
        total_study_time = request.data.get('total_study_time', 0)
        total_new_cards = request.data.get('total_new_cards', 0)
        total_learning_cards = request.data.get('total_learning_cards', 0)
        total_review_cards = request.data.get('total_review_cards', 0)

        if not video_id:
            return Response({'error': 'video_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 動画が既に存在するかチェック
        if Videos.objects.filter(video_id=video_id).exists():
            return Response({'message': 'Video already registered'}, status=status.HTTP_200_OK)

        # チャンネルが存在するかチェック
        channel = None
        if channel_id:
            from apps.channel_decks.models import Channeldecks
            try:
                channel = Channeldecks.objects.get(channel_id=channel_id)
            except Channeldecks.DoesNotExist:
                return Response({'error': 'Channel not found. Please register the channel first.'}, status=status.HTTP_404_NOT_FOUND)

        # 新しい動画を作成
        video = Videos.objects.create(
            video_id=video_id,
            channel=channel,
            total_study_time=total_study_time,
            total_new_cards=total_new_cards,
            total_learning_cards=total_learning_cards,
            total_review_cards=total_review_cards
        )
        serializer = VideosSerializer(video)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        # channel_idでフィルタリングが可能
        channel_id = request.GET.get('channel_id')

        if channel_id:
            videos = Videos.objects.filter(channel__channel_id=channel_id)
        else:
            videos = Videos.objects.all()

        serializer = VideosSerializer(videos, many=True)
        return Response(serializer.data)

    def delete(self, request, video_id, format=None):
        try:
            video = Videos.objects.get(video_id=video_id)
            video.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Videos.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)


class YoutubeTranscriptView(APIView):
    """
    YouTube動画の音声をダウンロードし、Gemini APIで文字起こしを行う

    実装手順:
    1. YouTubeから動画をダウンロードし、MP3/MP4音声ファイルに変換（pytubefix使用）
    2. Google AI StudioでGemini APIを利用する準備（APIキーは環境変数から）
    3. 音声ファイルをGemini File APIにアップロードして文字起こしを依頼
    4. APIレスポンスを受け取り、話者分けとタイムコード付きで整形
    """

    def get(self, request, video_id):
        logger.info(f"=== YouTube動画文字起こし開始: video_id={video_id} ===")

        try:
            # ステップ0: キャッシュ確認
            cache_key = f"transcript_gemini_{video_id}"
            cached_subtitles = cache.get(cache_key)
            if cached_subtitles:
                logger.info(f"キャッシュから字幕を取得")
                return Response({'subtitles': cached_subtitles}, status=status.HTTP_200_OK)

            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            subtitles = {}

            # ステップ1: YouTubeから音声をダウンロード（MP4/MP3形式）
            logger.info(f"ステップ1: YouTube動画から音声をダウンロード中...")
            from pytubefix import YouTube

            with tempfile.TemporaryDirectory() as temp_dir:
                # YouTube動画オブジェクトを作成
                yt = YouTube(youtube_url)
                logger.info(f"動画タイトル: {yt.title}")

                # 音声のみのストリームを取得（MP4形式を優先）
                audio_stream = yt.streams.filter(
                    only_audio=True,
                    file_extension='mp4'
                ).order_by('abr').desc().first()

                # MP4がない場合は他の音声フォーマットを試す
                if not audio_stream:
                    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

                if not audio_stream:
                    raise Exception("音声ストリームが見つかりませんでした")

                logger.info(f"音声ストリーム: {audio_stream.abr} - {audio_stream.mime_type}")

                # 音声をダウンロード
                # 注意: YouTube利用規約と著作権に注意してください
                audio_file_path = audio_stream.download(
                    output_path=temp_dir,
                    filename=f"{video_id}.mp4"
                )

                if not os.path.exists(audio_file_path) or os.path.getsize(audio_file_path) == 0:
                    raise Exception("音声ファイルのダウンロードに失敗しました")

                file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
                logger.info(f"音声ダウンロード完了: {audio_file_path} ({file_size_mb:.2f}MB)")

                # ファイルサイズが大きすぎる場合は警告
                MAX_FILE_SIZE_MB = 100  # Gemini APIの推奨上限
                if file_size_mb > MAX_FILE_SIZE_MB:
                    logger.warning(f"ファイルサイズが大きいため処理に時間がかかる可能性があります: {file_size_mb:.2f}MB")
                    # 音声を圧縮
                    try:
                        from pydub import AudioSegment
                        logger.info("音声ファイルを圧縮中...")
                        audio = AudioSegment.from_file(audio_file_path)
                        # ビットレートを下げて圧縮
                        compressed_path = os.path.join(temp_dir, f"{video_id}_compressed.mp3")
                        audio.export(compressed_path, format="mp3", bitrate="64k")

                        compressed_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
                        logger.info(f"圧縮完了: {compressed_size_mb:.2f}MB (元サイズ: {file_size_mb:.2f}MB)")
                        audio_file_path = compressed_path
                        file_size_mb = compressed_size_mb
                    except Exception as compress_error:
                        logger.warning(f"音声圧縮に失敗: {compress_error}。元のファイルを使用します")

                # ステップ2: Gemini APIのセットアップは完了（環境変数から読み込み済み）
                logger.info(f"ステップ2: Gemini API認証済み（APIキー: 環境変数から読み込み）")

                # ファイル形式に応じてmime_typeを設定
                mime_type = "audio/mp3" if audio_file_path.endswith(".mp3") else "audio/mp4"

                # ステップ3: 音声ファイルをGemini File APIにアップロード
                logger.info(f"ステップ3: Gemini File APIに音声をアップロード中... (サイズ: {file_size_mb:.2f}MB, 形式: {mime_type})")
                uploaded_file = genai.upload_file(audio_file_path, mime_type=mime_type)
                logger.info(f"アップロード完了: {uploaded_file.name}")

                # ファイル処理完了を待機
                max_wait_time = 300  # 5分に延長
                elapsed_time = 0
                while uploaded_file.state.name == "PROCESSING" and elapsed_time < max_wait_time:
                    logger.info(f"ファイル処理中... ({elapsed_time}秒経過)")
                    time.sleep(10)
                    elapsed_time += 10
                    try:
                        uploaded_file = genai.get_file(uploaded_file.name)
                    except Exception as e:
                        logger.warning(f"ファイル状態確認エラー: {e}")
                        time.sleep(5)
                        continue

                logger.info(f"最終ファイル状態: state={uploaded_file.state.name}")

                if uploaded_file.state.name == "FAILED":
                    error_details = getattr(uploaded_file, 'error', 'エラー詳細不明')
                    # ファイルを削除してクリーンアップ
                    try:
                        genai.delete_file(uploaded_file.name)
                    except:
                        pass
                    raise Exception(f"Gemini APIでファイル処理に失敗しました。動画が長すぎるか、形式が対応していない可能性があります。詳細: {error_details}")

                if uploaded_file.state.name != "ACTIVE":
                    try:
                        genai.delete_file(uploaded_file.name)
                    except:
                        pass
                    raise Exception(f"ファイル処理がタイムアウトしました。動画が長すぎる可能性があります。state={uploaded_file.state.name}")

                logger.info(f"ファイル処理完了: state={uploaded_file.state.name}")

                # Geminiモデルを初期化
                model = genai.GenerativeModel('gemini-2.0-flash-exp')

                # ステップ3-1: 日本語で文字起こし
                logger.info(f"ステップ3-1: 日本語で文字起こし中...")
                japanese_prompt = """
この音声ファイルを正確に日本語で文字起こししてください。

指示:
1. 話されている内容をすべて正確に日本語で書き起こす
2. タイムスタンプを [MM:SS] の形式で付ける（約5秒ごと、または話者が変わるタイミング）
3. 複数の話者がいる場合は「話者1:」「話者2:」のように話者を区別する
4. 各セグメントは改行で区切る
5. フォーマット: [MM:SS] 話者X: テキスト内容
6. 説明や前置きは不要、文字起こしのみを返す

例:
[00:00] 話者1: 皆さん、こんにちは。このビデオへようこそ
[00:05] 話者1: 今日は人工知能についてお話しします
[00:12] 話者2: それは面白そうですね。もっと詳しく教えてください
"""

                japanese_response = model.generate_content([japanese_prompt, uploaded_file])
                japanese_text = japanese_response.text.strip()
                logger.info(f"日本語文字起こし完了: {len(japanese_text)}文字")

                # ステップ3-2: 英語で文字起こし
                logger.info(f"ステップ3-2: 英語で文字起こし中...")
                english_prompt = """
この音声ファイルを正確に英語で文字起こししてください。

指示:
1. 話されている内容をすべて正確に英語で書き起こす
2. タイムスタンプを [MM:SS] の形式で付ける（約5秒ごと、または話者が変わるタイミング）
3. 複数の話者がいる場合は「Speaker 1:」「Speaker 2:」のように話者を区別する
4. 各セグメントは改行で区切る
5. フォーマット: [MM:SS] Speaker X: テキスト内容
6. 説明や前置きは不要、文字起こしのみを返す

例:
[00:00] Speaker 1: Hello everyone, welcome to this video
[00:05] Speaker 1: Today we're going to talk about artificial intelligence
[00:12] Speaker 2: That sounds interesting, can you tell me more?
"""

                english_response = model.generate_content([english_prompt, uploaded_file])
                english_text = english_response.text.strip()
                logger.info(f"英語文字起こし完了: {len(english_text)}文字")

                # ステップ4: タイムコードと話者分けを含む字幕に整形
                logger.info(f"ステップ4: 字幕データを整形中...")

                # 日本語字幕を整形
                japanese_entries = self._parse_transcript(japanese_text)
                subtitles['japanese'] = {
                    'text': japanese_text,
                    'transcript': japanese_entries,
                    'source': 'gemini_audio_transcription_japanese'
                }
                logger.info(f"日本語字幕整形完了: {len(japanese_entries)}エントリ")

                # 英語字幕を整形
                english_entries = self._parse_transcript(english_text)
                subtitles['english'] = {
                    'text': english_text,
                    'transcript': english_entries,
                    'source': 'gemini_audio_transcription_english'
                }
                logger.info(f"英語字幕整形完了: {len(english_entries)}エントリ")

                # アップロードしたファイルを削除
                genai.delete_file(uploaded_file.name)
                logger.info(f"一時ファイル削除完了")

            # キャッシュに保存（1時間）
            cache.set(cache_key, subtitles, 3600)
            logger.info(f"=== 文字起こし完了: {video_id} ===")

            return Response({'subtitles': subtitles}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"文字起こしエラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': f'文字起こしに失敗しました: {str(e)}',
                'video_id': video_id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _parse_transcript(self, text):
        """
        タイムスタンプ付きテキストをパースして構造化データに変換

        フォーマット: [MM:SS] 話者X: テキスト または [HH:MM:SS] Speaker X: Text
        """
        entries = []
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if line and '[' in line:
                # [MM:SS] または [HH:MM:SS] 形式に対応
                match = re.match(r'\[(\d+):(\d+)(?::(\d+))?\]\s*(.+)', line)
                if match:
                    if match.group(3):  # HH:MM:SS
                        hours = int(match.group(1))
                        minutes = int(match.group(2))
                        seconds = int(match.group(3))
                        start_time = hours * 3600 + minutes * 60 + seconds
                    else:  # MM:SS
                        minutes = int(match.group(1))
                        seconds = int(match.group(2))
                        start_time = minutes * 60 + seconds

                    text_content = match.group(4)

                    entries.append({
                        'start': start_time,
                        'duration': 5,  # デフォルト5秒
                        'text': text_content  # 話者情報を含む
                    })

        return entries


class HighlightView(APIView):
    """
    字幕ハイライト機能のCRUD API

    POST: ハイライトを作成（意味と語源を自動生成）
    GET: ハイライト一覧取得（video_idでフィルタ可能）
    """

    def post(self, request):
        """
        ハイライトを作成

        リクエストボディ:
        - video_id: 動画ID（必須）
        - highlighted_text: ハイライトした部分（必須、自動入力される）
        - timestamp: タイムスタンプ（秒）（必須）
        - auto_generate: 意味と語源を自動生成するか（デフォルト: true）
        """
        video_id = request.data.get('video_id')
        highlighted_text = request.data.get('highlighted_text')
        timestamp = request.data.get('timestamp')
        auto_generate = request.data.get('auto_generate', True)

        # バリデーション
        if not video_id or not highlighted_text or timestamp is None:
            return Response({
                'error': 'video_id, highlighted_text, timestamp are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 動画が存在するかチェック
        try:
            video = Videos.objects.get(video_id=video_id)
        except Videos.DoesNotExist:
            return Response({
                'error': 'Video not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # 意味と語源を自動生成
        meaning_japanese = request.data.get('meaning_japanese')
        etymology = request.data.get('etymology')
        image_url = request.data.get('image_url')

        if auto_generate and not (meaning_japanese and etymology):
            try:
                logger.info(f"Gemini APIで意味と語源を生成中: {highlighted_text}")
                generated_data = self._generate_meaning_and_etymology(highlighted_text)

                if not meaning_japanese:
                    meaning_japanese = generated_data.get('meaning_japanese')
                if not etymology:
                    etymology = generated_data.get('etymology')
                if not image_url:
                    image_url = generated_data.get('image_url')

                logger.info(f"生成完了: 意味={len(meaning_japanese or '')}文字, 語源={len(etymology or '')}文字")
            except Exception as e:
                logger.error(f"自動生成エラー: {str(e)}")
                # エラーが発生してもハイライトは保存する

        # ハイライトを作成
        highlight = Highlight.objects.create(
            video=video,
            highlighted_text=highlighted_text,
            timestamp=timestamp,
            meaning_japanese=meaning_japanese,
            etymology=etymology,
            image_url=image_url
        )

        serializer = HighlightSerializer(highlight)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """
        ハイライト一覧を取得

        クエリパラメータ:
        - video_id: 動画IDでフィルタ（オプション）
        """
        video_id = request.GET.get('video_id')

        if video_id:
            highlights = Highlight.objects.filter(video__video_id=video_id)
        else:
            highlights = Highlight.objects.all()

        serializer = HighlightSerializer(highlights, many=True)
        return Response(serializer.data)

    def _generate_meaning_and_etymology(self, highlighted_text):
        """
        Gemini APIを使って意味と語源を自動生成

        Args:
            highlighted_text: ハイライトされたテキスト（単語または英文）

        Returns:
            dict: {
                'meaning_japanese': '日本語の意味',
                'etymology': '語源の説明',
                'image_url': 'イメージ画像のURL（今後実装）'
            }
        """
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        prompt = f"""
以下の英語の単語または英文について、日本語で詳しく説明してください。

【テキスト】
{highlighted_text}

【指示】
1. **日本語の意味**: この単語または英文の意味を日本語で分かりやすく説明してください。複数の意味がある場合は主要なものを列挙してください。
2. **語源**: この単語の語源（etymology）を日本語で説明してください。ラテン語、ギリシャ語、古英語などの起源や、どのように現在の形になったかを説明してください。

【出力形式】
以下のJSON形式で出力してください（JSONコードブロックは不要、プレーンテキストのJSONのみ）:
{{
  "meaning_japanese": "日本語の意味の説明",
  "etymology": "語源の説明"
}}

※説明や前置きは不要です。JSONのみを返してください。
"""

        response = model.generate_content(prompt)
        response_text = response.text.strip()

        # JSONパース
        import json
        # コードブロックを削除
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        response_text = response_text.strip()

        try:
            data = json.loads(response_text)
            return {
                'meaning_japanese': data.get('meaning_japanese', ''),
                'etymology': data.get('etymology', ''),
                'image_url': None  # 今後実装: 画像生成APIを使用
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析エラー: {e}, レスポンス: {response_text}")
            # フォールバック: テキストをそのまま使用
            return {
                'meaning_japanese': response_text[:500],
                'etymology': '',
                'image_url': None
            }


class HighlightDetailView(APIView):
    """
    個別ハイライトの詳細・更新・削除

    GET: ハイライト詳細取得
    PUT: ハイライト更新
    PATCH: ハイライト部分更新
    DELETE: ハイライト削除
    """

    def get(self, request, highlight_id):
        """ハイライト詳細を取得"""
        try:
            highlight = Highlight.objects.get(id=highlight_id)
            serializer = HighlightSerializer(highlight)
            return Response(serializer.data)
        except Highlight.DoesNotExist:
            return Response({
                'error': 'Highlight not found'
            }, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, highlight_id):
        """ハイライトを更新"""
        try:
            highlight = Highlight.objects.get(id=highlight_id)
        except Highlight.DoesNotExist:
            return Response({
                'error': 'Highlight not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # 更新可能なフィールドのみを更新
        highlight.highlighted_text = request.data.get('highlighted_text', highlight.highlighted_text)
        highlight.timestamp = request.data.get('timestamp', highlight.timestamp)
        highlight.meaning_japanese = request.data.get('meaning_japanese', highlight.meaning_japanese)
        highlight.etymology = request.data.get('etymology', highlight.etymology)
        highlight.image_url = request.data.get('image_url', highlight.image_url)
        highlight.save()

        serializer = HighlightSerializer(highlight)
        return Response(serializer.data)

    def patch(self, request, highlight_id):
        """ハイライトを部分更新"""
        try:
            highlight = Highlight.objects.get(id=highlight_id)
        except Highlight.DoesNotExist:
            return Response({
                'error': 'Highlight not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # 送信されたフィールドのみを更新
        for field in ['highlighted_text', 'timestamp', 'meaning_japanese', 'etymology', 'image_url']:
            if field in request.data:
                setattr(highlight, field, request.data[field])

        highlight.save()

        serializer = HighlightSerializer(highlight)
        return Response(serializer.data)

    def delete(self, request, highlight_id):
        """ハイライトを削除"""
        try:
            highlight = Highlight.objects.get(id=highlight_id)
            highlight.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Highlight.DoesNotExist:
            return Response({
                'error': 'Highlight not found'
            }, status=status.HTTP_404_NOT_FOUND)
