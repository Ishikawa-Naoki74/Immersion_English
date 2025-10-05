#!/usr/bin/env python3

import os
import sys
import django

# Djangoの設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.videos.views import YoutubeTranscriptView

def test_youtube_transcript():
    """YouTubeTranscriptViewの動作をテスト"""
    
    # テスト用動画ID
    test_video_ids = [
        '30HgLRGDqKE',  # 登録済み動画
        'dQw4w9WgXcQ',  # Rick Astley - Never Gonna Give You Up
        '9bZkp7q19f0',  # PSY - GANGNAM STYLE
    ]
    
    view = YoutubeTranscriptView()
    
    for video_id in test_video_ids:
        print(f"\n{'='*50}")
        print(f"テスト動画ID: {video_id}")
        print('='*50)
        
        try:
            result = view.comprehensive_transcript_fetch(video_id)
            
            if result['success']:
                print("✅ 字幕取得成功！")
                data = result['data']
                subtitles = data.get('subtitles', {})
                
                for lang, subtitle_data in subtitles.items():
                    print(f"\n📝 {lang}字幕:")
                    print(f"   ソース: {subtitle_data['source']}")
                    print(f"   エントリ数: {len(subtitle_data['transcript'])}")
                    
                    # 最初の3つのエントリを表示
                    for i, entry in enumerate(subtitle_data['transcript'][:3]):
                        print(f"   [{i+1}] {entry['start']:.1f}s: {entry['text'][:50]}{'...' if len(entry['text']) > 50 else ''}")
                    
                    if len(subtitle_data['transcript']) > 3:
                        print(f"   ... さらに{len(subtitle_data['transcript']) - 3}個のエントリ")
                    
                    print(f"   全文(最初の200文字): {subtitle_data['text'][:200]}{'...' if len(subtitle_data['text']) > 200 else ''}")
                
                print(f"\n取得できた言語: {list(subtitles.keys())}")
                
            else:
                print(f"❌ 字幕取得失敗: {result['error']}")
                
        except Exception as e:
            print(f"💥 予期しないエラー: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("YouTube Transcript API テスト開始...")
    test_youtube_transcript()
    print("\nテスト完了!")