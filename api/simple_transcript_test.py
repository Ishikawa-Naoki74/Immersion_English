#!/usr/bin/env python
"""
简单的YouTube Transcript API 测试
"""
from youtube_transcript_api import YouTubeTranscriptApi

def test_basic_transcript_fetch(video_id='dQw4w9WgXcQ'):
    """基本的な字幕取得テスト"""
    print(f"=== YouTube字幕取得テスト: {video_id} ===")
    
    try:
        # APIインスタンスを作成
        api = YouTubeTranscriptApi()
        
        # 利用可能な字幕リストを取得
        print("利用可能な字幕リストを取得中...")
        transcript_list = api.list(video_id)
        
        print("利用可能な字幕:")
        for transcript in transcript_list:
            print(f"- {transcript.language_code} (Generated: {transcript.is_generated})")
        
        # 英語字幕を取得を試行
        for transcript in transcript_list:
            if transcript.language_code.startswith('en'):
                print(f"\n英語字幕({transcript.language_code})を取得中...")
                data = transcript.fetch()
                print(f"取得成功: {len(data)}個のエントリ")
                print("最初の3エントリ:")
                for i, entry in enumerate(data[:3]):
                    print(f"  {i+1}. {entry['start']:.2f}s: {entry['text']}")
                return True
        
        print("英語字幕が見つかりませんでした")
        return False
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return False

if __name__ == "__main__":
    video_id = 'dQw4w9WgXcQ'
    success = test_basic_transcript_fetch(video_id)
    print(f"テスト結果: {'成功' if success else '失敗'}")