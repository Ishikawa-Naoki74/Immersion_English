import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  { path: "/", name: "home", component: () => import("../views/Home.vue")},
  { path: "/register", name: "register", component: () => import("../views/Register.vue")},
  { path: "/login", name: "login", component: () => import("../views/Login.vue")},
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
