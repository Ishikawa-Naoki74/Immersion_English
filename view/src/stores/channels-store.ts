import { defineStore } from 'pinia'

export const useChannelsStore = defineStore('channels', {
  state: () => ({
    channels: [] as any[],
  }),
  actions: {
    setChannels(channelsData: any[]) {
      this.channels = channelsData;
    }
  }
})
