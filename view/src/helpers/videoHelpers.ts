import { Video } from '../types/video';

export function enhanceVideo(video: Video): Video & { isPlaying: boolean } {
  return {
    ...video,
    thumbnail: video.thumbnail.replace('default', 'hqdefault'),
    isPlaying: false
  };
}
