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
      { path: '/channels', name: 'search-channels-result', component: () => import('pages/SearchChannelsResult.vue')},
      { path: '/channel-decks', name: 'channel-decks', component: () => import('pages/ChannelDecks.vue')},
      { path: '/channel-videos', name: 'channel-videos', component: () => import('pages/ChannelVideos.vue')}
      ],
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;

