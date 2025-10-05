import os
import random
import time
import logging
import json
import tempfile
import subprocess
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from xml.etree.ElementTree import ParseError
from googletrans import Translator
import yt_dlp
from .models import Videos
from .serializers import VideosSerializer

# ロガーを設定
logger = logging.getLogger(__name__)


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
    def get(self, request, video_id):
        print(f"=== 字幕取得開始: video_id = {video_id} ===")
        logger.info(f"字幕取得開始: video_id = {video_id}")
        
        try:
            # より包括的な字幕取得戦略を実行
            result = self.comprehensive_transcript_fetch(video_id)
            
            if result['success']:
                print(f"レスポンスデータ作成完了")
                return Response(result['data'])
            else:
                print(f"=== エラー発生 ===\n{result['error']}")
                return Response({'error': result['error']}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            error_msg = f"予期しないエラー: {str(e)}"
            print(f"=== 予期しないエラー ===\n{error_msg}")
            logger.error(error_msg, exc_info=True)
            return Response({'error': error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def comprehensive_transcript_fetch(self, video_id):
        """youtube-transcript-apiを使用した包括的な字幕取得戦略"""
        print(f"=== YouTube字幕取得戦略開始: {video_id} ===")
        
        english_transcript = None
        japanese_transcript = None
        english_source = None
        japanese_source = None
        
        try:
            # Strategy 1: youtube-transcript-apiで直接字幕を取得
            print("=== 戦略1: youtube-transcript-apiで字幕取得 ===")
            
            # APIインスタンスを作成
            api = YouTubeTranscriptApi()
            
            # Strategy 1: 利用可能な字幕リストを取得
            print("=== 利用可能な字幕リストを取得中 ===")
            transcript_list = api.list(video_id)
            
            # 英語字幕を探す
            print("=== 英語字幕を探索 ===")
            for transcript in transcript_list:
                try:
                    if transcript.language_code.startswith('en') or transcript.language_code == 'en':
                        print(f"英語字幕発見: {transcript.language_code} - Generated: {transcript.is_generated}")
                        data = transcript.fetch()
                        
                        english_transcript = []
                        for entry in data:
                            english_transcript.append({
                                'text': entry['text'].strip(),
                                'start': entry['start'],
                                'duration': entry['duration']
                            })
                        english_source = 'auto-generated' if transcript.is_generated else 'original'
                        print(f"英語字幕取得成功({transcript.language_code}): {len(english_transcript)}個のエントリ")
                        break
                        
                except Exception as e:
                    print(f"英語字幕取得エラー({transcript.language_code}): {str(e)}")
                    if "blocking requests from your IP" in str(e):
                        return {'success': False, 'error': 'YouTubeからのアクセスが制限されています。しばらく時間をおいてから再度お試しください。'}
                    continue
            
            # 日本語字幕を探す
            print("=== 日本語字幕を探索 ===")
            for transcript in transcript_list:
                try:
                    if transcript.language_code.startswith('ja') or transcript.language_code == 'ja':
                        print(f"日本語字幕発見: {transcript.language_code} - Generated: {transcript.is_generated}")
                        data = transcript.fetch()
                        
                        japanese_transcript = []
                        for entry in data:
                            japanese_transcript.append({
                                'text': entry['text'].strip(),
                                'start': entry['start'],
                                'duration': entry['duration']
                            })
                        japanese_source = 'auto-generated' if transcript.is_generated else 'original'
                        print(f"日本語字幕取得成功({transcript.language_code}): {len(japanese_transcript)}個のエントリ")
                        break
                        
                except Exception as e:
                    print(f"日本語字幕取得エラー({transcript.language_code}): {str(e)}")
                    if "blocking requests from your IP" in str(e):
                        return {'success': False, 'error': 'YouTubeからのアクセスが制限されています。しばらく時間をおいてから再度お試しください。'}
                    continue
            
            # Strategy 2: 利用可能な任意の言語から翻訳
            if not english_transcript or not japanese_transcript:
                print("=== 戦略2: 利用可能な字幕から翻訳 ===")
                for transcript in transcript_list:
                    try:
                        print(f"利用可能な字幕を発見: {transcript.language_code}")
                        data = transcript.fetch()
                        
                        base_transcript = []
                        for entry in data:
                            base_transcript.append({
                                'text': entry['text'].strip(),
                                'start': entry['start'],
                                'duration': entry['duration']
                            })
                        
                        # 必要に応じて翻訳
                        if not english_transcript and transcript.language_code not in ['en']:
                            print(f"{transcript.language_code}→英語翻訳中...")
                            english_transcript = self.translate_transcript(base_transcript, 'en')
                            english_source = f'translated_from_{transcript.language_code}'
                            print(f"英語翻訳完了: {len(english_transcript)}個のエントリ")
                        elif not english_transcript and transcript.language_code == 'en':
                            english_transcript = base_transcript
                            english_source = 'auto-generated' if transcript.is_generated else 'original'
                        
                        if not japanese_transcript and transcript.language_code not in ['ja']:
                            print(f"{transcript.language_code}→日本語翻訳中...")
                            japanese_transcript = self.translate_transcript(base_transcript, 'ja')
                            japanese_source = f'translated_from_{transcript.language_code}'
                            print(f"日本語翻訳完了: {len(japanese_transcript)}個のエントリ")
                        elif not japanese_transcript and transcript.language_code == 'ja':
                            japanese_transcript = base_transcript
                            japanese_source = 'auto-generated' if transcript.is_generated else 'original'
                        
                        # 両方取得できたら終了
                        if english_transcript and japanese_transcript:
                            break
                            
                    except Exception as e:
                        print(f"字幕({transcript.language_code})の取得エラー: {str(e)}")
                        if "blocking requests from your IP" in str(e):
                            return {'success': False, 'error': 'YouTubeからのアクセスが制限されています。しばらく時間をおいてから再度お試しください。'}
                        continue
            
            # Strategy 4: 個別翻訳フォールバック
            if english_transcript and not japanese_transcript:
                print("=== 戦略4: 英語→日本語翻訳 ===")
                japanese_transcript = self.translate_transcript(english_transcript, 'ja')
                japanese_source = 'translated_from_english'
                print(f"英語→日本語翻訳完了: {len(japanese_transcript)}個のエントリ")
            
            if japanese_transcript and not english_transcript:
                print("=== 戦略4: 日本語→英語翻訳 ===")
                english_transcript = self.translate_transcript(japanese_transcript, 'en')
                english_source = 'translated_from_japanese'
                print(f"日本語→英語翻訳完了: {len(english_transcript)}個のエントリ")
        
        except Exception as e:
            print(f"字幕取得中の予期しないエラー: {str(e)}")
            logger.error(f"字幕取得中の予期しないエラー: {str(e)}", exc_info=True)
        
        # レスポンスデータを構築
        response_data = {
            'video_id': video_id,
            'subtitles': {}
        }
        
        if english_transcript:
            response_data['subtitles']['english'] = {
                'transcript': english_transcript,
                'source': english_source,
                'text': ' '.join([item['text'] for item in english_transcript])
            }
        
        if japanese_transcript:
            response_data['subtitles']['japanese'] = {
                'transcript': japanese_transcript, 
                'source': japanese_source,
                'text': ' '.join([item['text'] for item in japanese_transcript])
            }
        
        if not response_data['subtitles']:
            return {'success': False, 'error': '字幕の取得に失敗しました。利用可能な字幕がありません。'}
        
        print(f"字幕取得成功: {list(response_data['subtitles'].keys())}")
        return {'success': True, 'data': response_data}
    
    
    def translate_transcript(self, transcript, target_lang):
        """Googletransを使用して字幕を翻訳"""
        translated_transcript = []
        
        try:
            translator = Translator()
            
            # バッチ翻訳のためのテキストを準備
            texts_to_translate = [entry['text'] for entry in transcript]
            
            # 大きなバッチを小さく分割して翻訳
            batch_size = 10
            translated_texts = []
            
            for i in range(0, len(texts_to_translate), batch_size):
                batch = texts_to_translate[i:i+batch_size]
                try:
                    # バッチ翻訳
                    translations = translator.translate(batch, dest=target_lang)
                    
                    if isinstance(translations, list):
                        translated_texts.extend([t.text for t in translations])
                    else:
                        translated_texts.append(translations.text)
                    
                    # API制限を避けるため少し待機
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"翻訳バッチエラー: {str(e)}")
                    # エラーの場合は元のテキストを使用
                    translated_texts.extend(batch)
            
            # 翻訳結果を元のトランスクリプト構造に組み込み
            for i, entry in enumerate(transcript):
                if i < len(translated_texts):
                    translated_transcript.append({
                        'text': translated_texts[i],
                        'start': entry['start'],
                        'duration': entry['duration']
                    })
                else:
                    # 翻訳がない場合は元のテキストを使用
                    translated_transcript.append(entry)
        
        except Exception as e:
            print(f"翻訳エラー: {str(e)}")
            logger.error(f"翻訳エラー: {str(e)}", exc_info=True)
            # 翻訳に失敗した場合は元のトランスクリプトを返す
            return transcript
        
        return translated_transcript


class TestView(APIView):
    def get(self, request):
        print("=== テストエンドポイントが呼び出されました ===")
        return Response({
            'message': 'テスト成功',
            'status': 'ok',
            'timestamp': time.time()
        })
