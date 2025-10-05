import os
import random
import time
import logging
import subprocess
import tempfile
import re
from django.core.cache import cache
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Videos
from .serializers import VideosSerializer
import google.generativeai as genai

# ロガーを設定
logger = logging.getLogger(__name__)

# Gemini APIの設定
genai.configure(api_key=settings.GEMINI_API_KEY)


class VideosView(APIView):
    def post(self, request):
        video_id = request.data.get('video_id')
        channel_id = request.data.get('channel_id', 'unknown')
        total_study_time = request.data.get('total_study_time', 0)
        total_new_cards = request.data.get('total_new_cards', 0)
        total_learning_cards = request.data.get('total_learning_cards', 0)
        total_review_cards = request.data.get('total_review_cards', 0)
        
        if not video_id:
            return Response({'error': 'video_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 動画が既に存在するかチェック
        if Videos.objects.filter(video_id=video_id).exists():
            return Response({'error': 'Video already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 新しい動画を作成
        video = Videos.objects.create(
            video_id=video_id,
            channel_id=channel_id,
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
            videos = Videos.objects.filter(channel_id=channel_id)
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

    手順:
    1. YouTube動画からMP4/MP3音声をダウンロード（pytubefix使用）
    2. Gemini File APIに音声をアップロード
    3. Gemini APIで音声を日本語と英語で文字起こし
    4. タイムスタンプと話者分けを含む字幕を生成
    """
    def get(self, request, video_id):
        print(f"=== Gemini APIで音声解析開始: video_id = {video_id} ===")
        logger.info(f"Gemini APIで音声解析開始: video_id = {video_id}")

        try:
            # キャッシュキーを生成
            cache_key = f"transcript_gemini_{video_id}"

            # キャッシュから字幕を取得
            cached_subtitles = cache.get(cache_key)
            if cached_subtitles:
                logger.info(f"キャッシュから字幕を取得: {video_id}")
                return Response({'subtitles': cached_subtitles}, status=status.HTTP_200_OK)

            subtitles = {}
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"

            # Gemini APIで音声を解析
            logger.info(f"=== pytubefixで音声ダウンロードと文字起こしを開始 ===")

            try:
                from pytubefix import YouTube

                with tempfile.TemporaryDirectory() as temp_dir:
                    # 1. pytubefixで音声をダウンロード
                    logger.info(f"ステップ1: pytubefixで音声ダウンロード中...")

                    yt = YouTube(youtube_url)
                    logger.info(f"動画タイトル: {yt.title}")

                    # 音声ストリームを取得（最も高品質な音声）
                    audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()

                    if not audio_stream:
                        # mp4がない場合は他の音声フォーマットを試す
                        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

                    if not audio_stream:
                        raise Exception(f"音声ストリームが見つかりませんでした")

                    logger.info(f"音声ストリーム: {audio_stream.abr} - {audio_stream.mime_type}")

                    # 音声をダウンロード
                    audio_file = audio_stream.download(output_path=temp_dir, filename=f"{video_id}.mp4")

                    if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
                        raise Exception(f"音声ファイルのダウンロードに失敗しました")

                    logger.info(f"音声ダウンロード完了: {audio_file} (サイズ: {os.path.getsize(audio_file)} bytes)")

                    # 2. Gemini APIに音声をアップロード
                    logger.info(f"ステップ2: Gemini APIに音声アップロード中...")

                    uploaded_file = genai.upload_file(audio_file)
                    logger.info(f"音声アップロード完了: {uploaded_file.name}")

                    # ファイルが処理されるまで待機
                    max_wait_time = 120  # 最大2分待機
                    elapsed_time = 0
                    while uploaded_file.state.name == "PROCESSING" and elapsed_time < max_wait_time:
                        logger.info(f"ファイル処理中... ({elapsed_time}秒経過)")
                        time.sleep(5)
                        elapsed_time += 5
                        uploaded_file = genai.get_file(uploaded_file.name)

                    if uploaded_file.state.name == "FAILED":
                        raise Exception(f"ファイル処理失敗: state={uploaded_file.state.name}")

                    if uploaded_file.state.name == "PROCESSING":
                        logger.warning(f"タイムアウト: ファイル処理に時間がかかりすぎています")
                        # それでも処理を続行

                    logger.info(f"ファイル処理完了: state={uploaded_file.state.name}")

                    # 3. Geminiで音声を文字起こし（英語と日本語）
                    logger.info(f"ステップ3: Geminiで音声文字起こし中...")
                    model = genai.GenerativeModel('gemini-2.0-flash-exp')

                    # 英語文字起こし
                    english_transcription_prompt = """
この音声ファイルを正確に英語で文字起こししてください。

指示:
1. 話されている内容をすべて正確に書き起こす
2. タイムスタンプを [MM:SS] の形式で付ける（5秒ごとまたは話者が変わるタイミング）
3. 複数の話者がいる場合は「Speaker 1:」「Speaker 2:」のように話者を区別する
4. 各セグメントは改行で区切る
5. フォーマット: [MM:SS] Speaker X: テキスト内容
6. 説明や前置きは不要、文字起こしのみを返す

例:
[00:00] Speaker 1: Hello everyone, welcome to this video
[00:05] Speaker 1: Today we're going to talk about artificial intelligence
[00:12] Speaker 2: That sounds interesting, can you tell me more?
"""

                    logger.info(f"英語文字起こし実行中（時間がかかる場合があります）...")
                    response = model.generate_content([english_transcription_prompt, uploaded_file])
                    english_text = response.text.strip()

                    logger.info(f"英語文字起こし完了: {len(english_text)}文字")

                    # 日本語文字起こし
                    japanese_transcription_prompt = """
この音声ファイルを正確に日本語で文字起こししてください。

指示:
1. 話されている内容をすべて正確に日本語で書き起こす
2. タイムスタンプを [MM:SS] の形式で付ける（5秒ごとまたは話者が変わるタイミング）
3. 複数の話者がいる場合は「話者1:」「話者2:」のように話者を区別する
4. 各セグメントは改行で区切る
5. フォーマット: [MM:SS] 話者X: テキスト内容
6. 説明や前置きは不要、文字起こしのみを返す
7. 自然な日本語に翻訳する

例:
[00:00] 話者1: 皆さん、こんにちは。このビデオへようこそ
[00:05] 話者1: 今日は人工知能についてお話しします
[00:12] 話者2: それは面白そうですね。もっと詳しく教えてください
"""

                    logger.info(f"日本語文字起こし実行中...")
                    japanese_response = model.generate_content([japanese_transcription_prompt, uploaded_file])
                    japanese_direct_text = japanese_response.text.strip()

                    logger.info(f"日本語文字起こし完了: {len(japanese_direct_text)}文字")

                    # 4. タイムコード付き字幕に整形（英語）
                    logger.info(f"ステップ4: 英語字幕を整形中...")
                    transcript_entries = []
                    lines = english_text.split('\n')

                    for line in lines:
                        line = line.strip()
                        if line and '[' in line:
                            # [MM:SS] または [HH:MM:SS] 形式に対応、話者情報も含む
                            match = re.match(r'\[(\d+):(\d+)(?::(\d+))?\]\s*(.+)', line)
                            if match:
                                if match.group(3):  # HH:MM:SS
                                    hours = int(match.group(1))
                                    minutes = int(match.group(2))
                                    seconds = int(match.group(3))
                                    start_time = hours * 3600 + minutes * 60 + seconds
                                    text = match.group(4)
                                else:  # MM:SS
                                    minutes = int(match.group(1))
                                    seconds = int(match.group(2))
                                    start_time = minutes * 60 + seconds
                                    text = match.group(4)

                                transcript_entries.append({
                                    'start': start_time,
                                    'duration': 5,
                                    'text': text  # 話者情報を含む
                                })

                    subtitles['english'] = {
                        'text': english_text,
                        'transcript': transcript_entries if transcript_entries else None,
                        'source': 'gemini_audio_transcription_with_speakers'
                    }

                    logger.info(f"英語字幕完成: {len(transcript_entries)}エントリ")

                    # 5. 日本語字幕を整形
                    logger.info(f"ステップ5: 日本語字幕を整形中...")
                    japanese_entries = []
                    lines = japanese_direct_text.split('\n')

                    for line in lines:
                        line = line.strip()
                        if line and '[' in line:
                            match = re.match(r'\[(\d+):(\d+)(?::(\d+))?\]\s*(.+)', line)
                            if match:
                                if match.group(3):
                                    hours = int(match.group(1))
                                    minutes = int(match.group(2))
                                    seconds = int(match.group(3))
                                    start_time = hours * 3600 + minutes * 60 + seconds
                                    text = match.group(4)
                                else:
                                    minutes = int(match.group(1))
                                    seconds = int(match.group(2))
                                    start_time = minutes * 60 + seconds
                                    text = match.group(4)

                                japanese_entries.append({
                                    'start': start_time,
                                    'duration': 5,
                                    'text': text  # 話者情報を含む
                                })

                    subtitles['japanese'] = {
                        'text': japanese_direct_text,
                        'transcript': japanese_entries if japanese_entries else transcript_entries,
                        'source': 'gemini_audio_transcription_japanese_with_speakers'
                    }

                    logger.info(f"日本語字幕完成: {len(japanese_entries)}エントリ")

                    # アップロードしたファイルを削除
                    genai.delete_file(uploaded_file.name)
                    logger.info(f"一時ファイル削除完了")

            except Exception as audio_error:
                logger.error(f"音声解析エラー: {str(audio_error)}")
                import traceback
                traceback.print_exc()
                return Response({'error': f'音声解析に失敗しました: {str(audio_error)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 字幕をキャッシュに保存（1時間）
            if subtitles:
                cache.set(cache_key, subtitles, 3600)
                logger.info(f"字幕をキャッシュに保存しました")
                return Response({'subtitles': subtitles}, status=status.HTTP_200_OK)

            return Response({
                'error': '字幕を取得できませんでした',
                'video_id': video_id
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"字幕取得エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'error': f'字幕の取得中にエラーが発生しました: {str(e)}',
                'video_id': video_id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestView(APIView):
    def get(self, request):
        print("=== テストエンドポイントが呼び出されました ===")
        return Response({
            'message': 'テスト成功',
            'status': 'ok',
            'timestamp': time.time()
        })