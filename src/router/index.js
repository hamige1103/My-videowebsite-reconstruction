import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router';

const routes = [
  {
    path: '/',
    component: () => import('../views/MovieHome.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/personSapce/:user_id',
    name: 'personSapce',
    component: () => import('../views/PersonalSapcePage.vue'),
    props: true,
    meta: {
      title: "用户空间",
      needLogin: true //需要登录
    }
  },
  {
    path: '/movtype/:movtype',
    component:  () => import('../views/MoviePage.vue'),
    props: true
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('../views/MovieKeywordPage.vue')
  },
  {
    path: '/smart-search',
    name: 'smart-search',
    component: () => import('../views/SmartSearchPage.vue')
  },
  {
    path: '/movdetail/:vod_id',
    name: 'movdetail',
    component: () => import('../views/MovDetailPage.vue'),
    props: true
  },
  {
    path: '/live',
    name: 'LiveHome',
    component: () => import('../views/LiveHome.vue')
  },
  {
    path: '/live/create',
    name: 'LiveCreate',
    component: () => import('../views/LiveCreate.vue')
  },
  {
    path: '/live/watch',
    name: 'LiveWatch',
    component: () => import('../views/LiveWatch.vue')
  },
  {
    path: '/live/stream',
    name: 'LiveStream',
    component: () => import('../views/LiveStream.vue')
  },
  {
    path: '/admin/test',
    name: 'admin-test',
    component: () => import('../views/AdminTest.vue'),
    meta: {
      title: "管理后台测试"
    }
  },
  // 管理后台路由
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminLayout.vue'),
    meta: {
      title: "管理后台",
      needLogin: true,
      needAdmin: true //需要管理员权限
    },
    redirect: '/admin/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'admin-dashboard',
        component: () => import('../views/AdminDashboard.vue'),
        meta: { title: "仪表盘" }
      },
      {
        path: 'users',
        name: 'admin-users',
        component: () => import('../views/AdminUsers.vue'),
        meta: { title: "用户管理" }
      },
      {
        path: 'videos',
        name: 'admin-videos',
        component: () => import('../views/AdminVideos.vue'),
        meta: { title: "视频管理" }
      },
      {
        path: 'comments',
        name: 'admin-comments',
        component: () => import('../views/AdminComments.vue'),
        meta: { title: "评论管理" }
      }
    ]
  }
];


const router = createRouter({
  // history: createWebHashHistory(),  // hash路由模式
  history: createWebHistory(),  // history路由模式
  routes
});

// 全局路由守卫
router.beforeEach((to, from, next) => {
  let token = localStorage.getItem('token')
  
  // 检查是否需要登录
  if (to.meta.needLogin) {
    if (token) {
      // 检查是否需要管理员权限
      if (to.meta.needAdmin) {
        const userInfo = localStorage.getItem('userInfo')
        if (userInfo) {
          try {
            const user = JSON.parse(userInfo)
            if (user.role === 'admin') {
              next()
            } else {
              alert('您没有管理员权限，无法访问管理后台')
              next('/') // 跳转到首页
            }
          } catch (error) {
            console.error('解析用户信息失败:', error)
            next('/login')
          }
        } else {
          next('/login')
        }
      } else {
        next()
      }
    } else {
      next({path: '/login'}) //跳转到登录页
    }
  } else {
    next()
  }
})

export default router;
