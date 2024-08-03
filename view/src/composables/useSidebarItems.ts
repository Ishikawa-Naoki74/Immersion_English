import { ref } from 'vue';
import { fabYoutube } from '@quasar/extras/fontawesome-v6';

export function useSidebarItems() {
  const sidebarItems = ref([
    {
      items: [
        { icon: 'home', label: 'Home' },
        { icon: 'whatshot', label: 'Trending' },
        { icon: 'subscriptions', label: 'Subscriptions' },
      ]
    },
    {
      items: [
        { icon: 'folder', label: 'Library' },
        { icon: 'restore', label: 'History' },
        { icon: 'watch_later', label: 'Watch later' },
        { icon: 'thumb_up_alt', label: 'Liked videos' },
      ]
    },
    {
      items: [
        { icon: fabYoutube, label: 'YouTube Premium' },
        { icon: 'local_movies', label: 'Movies & Shows' },
        { icon: 'videogame_asset', label: 'Gaming' },
        { icon: 'live_tv', label: 'Live' },
      ]
    },
    {
      items: [
        { icon: 'settings', text: 'Settings' },
        { icon: 'flag', text: 'Report history' },
        { icon: 'help', text: 'Help' },
        { icon: 'feedback', text: 'Send feedback' },
      ]
    }
  ])

 return {
  sidebarItems
 }
}
