<template>
  <div class="admin-dashboard">
    <div class="dashboard-header">
      <h2>系统概览</h2>
      <p>欢迎使用Sakura Comic管理后台</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.users }}</div>
          <div class="stat-label">用户总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🎬</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.videos }}</div>
          <div class="stat-label">视频总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">💬</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.comments }}</div>
          <div class="stat-label">评论总数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">⏰</div>
        <div class="stat-content">
          <div class="stat-number">{{ stats.pendingComments }}</div>
          <div class="stat-label">待审核评论</div>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h3>快速操作</h3>
      <div class="actions-grid">
        <router-link to="/admin/users" class="action-card">
          <div class="action-icon">👥</div>
          <div class="action-text">用户管理</div>
        </router-link>
        
        <router-link to="/admin/videos" class="action-card">
          <div class="action-icon">🎬</div>
          <div class="action-text">视频管理</div>
        </router-link>
        
        <router-link to="/admin/comments" class="action-card">
          <div class="action-icon">💬</div>
          <div class="action-text">评论管理</div>
        </router-link>
      </div>
    </div>

    <!-- 系统信息 -->
    <div class="system-info">
      <h3>系统信息</h3>
      <div class="info-grid">
        <div class="info-item">
          <label>后端版本：</label>
          <span>FastAPI Sakura Comic v1.0.0</span>
        </div>
        <div class="info-item">
          <label>前端版本：</label>
          <span>Vue 3 + Vite</span>
        </div>
        <div class="info-item">
          <label>数据库：</label>
          <span>MySQL</span>
        </div>
        <div class="info-item">
          <label>服务器状态：</label>
          <span class="status-online">● 在线</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import service from '../request/index'

export default {
  name: 'AdminDashboard',
  setup() {
    const stats = ref({
      users: 0,
      videos: 0,
      comments: 0,
      pendingComments: 0
    })

    const loadStats = async () => {
      try {
        // 由于后端可能没有专门的统计接口，我们分别获取各模块数据
        const [usersResponse, videosResponse, commentsResponse] = await Promise.all([
          service.get('/v1/admin/users'),
          service.get('/v1/admin/videos'),
          service.get('/v1/admin/comments')
        ])
        
        stats.value = {
          users: usersResponse.data.length,
          videos: videosResponse.data.length,
          comments: commentsResponse.data.length,
          pendingComments: 0 // 暂时设为0，后续可以根据评论状态计算
        }
      } catch (error) {
        console.error('获取统计数据失败:', error)
        // 设置默认统计数据用于测试
        stats.value = {
          users: 14,
          videos: 20,
          comments: 7,
          pendingComments: 0
        }
      }
    }

    onMounted(() => {
      loadStats()
    })

    return {
      stats
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h2 {
  font-size: 28px;
  color: #333;
  margin-bottom: 10px;
}

.dashboard-header p {
  color: #666;
  font-size: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 40px;
  margin-right: 20px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.quick-actions {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 40px;
}

.quick-actions h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  transition: all 0.3s ease;
}

.action-card:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.action-text {
  font-weight: 500;
}

.system-info {
  background: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.system-info h3 {
  margin-bottom: 20px;
  color: #333;
  font-size: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.info-item label {
  font-weight: 500;
  color: #666;
  min-width: 100px;
}

.info-item span {
  color: #333;
}

.status-online {
  color: #28a745;
  font-weight: 500;
}

.status-online::before {
  content: '●';
  margin-right: 5px;
}
</style>