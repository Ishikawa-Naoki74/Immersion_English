#!/usr/bin/env python3

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

def test_transcript_api():
    # テスト用の動画ID（字幕があることで有名な動画）
    test_video_ids = [
        'dQw4w9WgXcQ',  # Rick Astley - Never Gonna Give You Up
        '9bZkp7q19f0',  # PSY - GANGNAM STYLE  
        'kJQP7kiw5Fk',  # Despacito
        'fJ9rUzIMcZQ',  # Queen - Bohemian Rhapsody
        '30HgLRGDqKE',  # 登録されている動画ID
    ]
    
    for video_id in test_video_ids:
        print(f"\n=== Testing video ID: {video_id} ===")
        
        try:
            # まず利用可能な字幕リストを取得
            print("Trying to list available transcripts...")
            transcript_list = YouTubeTranscriptApi().list(video_id)
            print(f"Transcript list type: {type(transcript_list)}")
            print(f"Available transcripts:")
            
            for transcript in transcript_list:
                print(f"  - Language: {transcript.language_code} ({transcript.language})")
                print(f"    Generated: {transcript.is_generated}")
                print(f"    Translatable: {transcript.is_translatable}")
                
                # 最初の字幕を取得してテスト
                try:
                    data = transcript.fetch()
                    print(f"    Fetched {len(data)} entries")
                    if data:
                        first_entry = data[0]
                        print(f"    First entry type: {type(first_entry)}")
                        print(f"    First entry attributes: {dir(first_entry)}")
                        if hasattr(first_entry, 'text'):
                            print(f"    Sample text: {first_entry.text[:50]}...")
                        if hasattr(first_entry, 'start'):
                            print(f"    Start time: {first_entry.start}")
                        if hasattr(first_entry, 'duration'):
                            print(f"    Duration: {first_entry.duration}")
                    break  # 最初の字幕が取得できたら終了
                except Exception as fetch_error:
                    print(f"    Fetch failed: {fetch_error}")
                    
        except TranscriptsDisabled:
            print("Transcripts are disabled for this video")
        except VideoUnavailable:
            print("Video is unavailable")
        except NoTranscriptFound:
            print("No transcript found")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing YouTube Transcript API...")
    test_transcript_api()
    print("\nTest completed.")