<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2>Sakura Comic 管理后台</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link 
          to="/admin/dashboard" 
          class="nav-item"
          :class="{ active: $route.path === '/admin/dashboard' }"
        >
          <i class="icon">📊</i>
          <span>仪表盘</span>
        </router-link>
        <router-link 
          to="/admin/users" 
          class="nav-item"
          :class="{ active: $route.path === '/admin/users' }"
        >
          <i class="icon">👥</i>
          <span>用户管理</span>
        </router-link>
        <router-link 
          to="/admin/videos" 
          class="nav-item"
          :class="{ active: $route.path === '/admin/videos' }"
        >
          <i class="icon">🎬</i>
          <span>视频管理</span>
        </router-link>
        <router-link 
          to="/admin/comments" 
          class="nav-item"
          :class="{ active: $route.path === '/admin/comments' }"
        >
          <i class="icon">💬</i>
          <span>评论管理</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <button @click="logout" class="logout-btn">
          <i class="icon">🚪</i>
          <span>退出登录</span>
        </button>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 顶部导航栏 -->
      <header class="top-header">
        <div class="header-left">
          <h1>{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <span class="user-info">欢迎，{{ userInfo?.name || '管理员' }}</span>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { localGet, localRemove } from '../utils'

export default {
  name: 'AdminLayout',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const userInfo = ref(null)

    // 计算页面标题
    const pageTitle = computed(() => {
      const titles = {
        '/admin/dashboard': '仪表盘',
        '/admin/users': '用户管理',
        '/admin/videos': '视频管理',
        '/admin/comments': '评论管理'
      }
      return titles[route.path] || '管理后台'
    })

    // 检查管理员权限
    const checkAdminPermission = () => {
      const token = localGet('token')
      const user = localGet('userInfo')
      
      if (!token) {
        router.push('/login')
        return false
      }
      
      if (user) {
        userInfo.value = JSON.parse(user)
        // 检查用户角色是否为管理员
        if (userInfo.value.role !== 'admin') {
          router.push('/')
          return false
        }
      }
      
      return true
    }

    // 退出登录
    const logout = () => {
      localRemove('token')
      localRemove('userInfo')
      router.push('/login')
    }

    onMounted(() => {
      checkAdminPermission()
    })

    return {
      userInfo,
      pageTitle,
      logout
    }
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background-color: #f5f5f5;
}

.sidebar {
  width: 250px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border-left-color: white;
}

.nav-item .icon {
  margin-right: 10px;
  font-size: 18px;
}

.sidebar-footer {
  padding: 20px;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 10px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 5px;
  color: white;
  cursor: pointer;
  transition: background 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-header {
  background: white;
  padding: 0 30px;
  height: 70px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.top-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.user-info {
  color: #666;
  font-size: 14px;
}

.content {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background-color: #f8f9fa;
}
</style>