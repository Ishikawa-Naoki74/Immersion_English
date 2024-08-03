import { defineStore } from 'pinia'

export const useVideosStore = defineStore('videos', {
  state: () => ({
    videos: [] as any[],
  }),
  actions: {
    setVideos(videosData: any[]) {
      this.videos = videosData;
    }
  }
})
