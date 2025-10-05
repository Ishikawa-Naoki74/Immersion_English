import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    component: () => import('pages/UserForm.vue')
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'home', component: () => import('pages/ChannelDecks.vue')},
      { path: '/channels', name: 'search-channels-result', component: () => import('pages/SearchChannelsResult.vue')},
      { path: '/channel-decks', name: 'channel-decks', component: () => import('pages/ChannelDecks.vue')},
      { path: '/channel-videos', name: 'channel-videos', component: () => import('pages/ChannelVideos.vue')},
      { path: '/channel-videos/:channelId', name: 'channel-videos-by-id', component: () => import('pages/ChannelVideos.vue')},
      { path: '/video-decks', name: 'video-decks', component: () => import('pages/VideoDecks.vue')}
      ],
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;

