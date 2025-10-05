#!/usr/bin/env python3

from youtube_transcript_api import YouTubeTranscriptApi
import time
import random

def test_simple_transcript():
    # 登録済みの動画IDを使用
    test_video_ids = [
        '30HgLRGDqKE',
        '5a-SiHzIxuk', 
        'SnP0KDrmtNM'
    ]
    
    # APIインスタンスを作成
    ytt_api = YouTubeTranscriptApi()
    
    for video_id in test_video_ids:
        print(f"\n=== Testing video ID: {video_id} ===")
        
        try:
            # レート制限を避けるためのランダムな遅延
            time.sleep(random.uniform(1, 3))
            
            # 字幕リストを取得
            transcript_list = ytt_api.list(video_id)
            print(f"字幕リスト取得成功")
            
            # 利用可能な字幕を表示
            available_transcripts = []
            for transcript in transcript_list:
                transcript_info = {
                    'language_code': transcript.language_code,
                    'language': transcript.language,
                    'is_generated': transcript.is_generated,
                    'is_translatable': transcript.is_translatable
                }
                available_transcripts.append(transcript_info)
                print(f"  - {transcript_info['language_code']}: {transcript_info['language']}")
                print(f"    Generated: {transcript_info['is_generated']}")
                print(f"    Translatable: {transcript_info['is_translatable']}")
            
            # 最初の字幕を試しに取得
            if available_transcripts:
                first_transcript = next(iter(transcript_list))
                print(f"\n最初の字幕({first_transcript.language_code})を取得中...")
                data = first_transcript.fetch()
                print(f"字幕取得成功: {len(data)}個のエントリ")
                
                # サンプルデータを表示
                if data:
                    sample_entry = data[0]
                    print(f"サンプルエントリ: {sample_entry}")
                    print(f"テキスト: {sample_entry['text']}")
                    print(f"開始時刻: {sample_entry['start']}")
                    print(f"継続時間: {sample_entry['duration']}")
                    break  # 成功したら次の動画へ
                    
        except Exception as e:
            print(f"エラー: {str(e)}")
            
    print("\nテスト完了")

if __name__ == "__main__":
    test_simple_transcript()