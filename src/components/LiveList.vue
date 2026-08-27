<template>
  <div class="live-list-container">
    <div class="live-list-header">
      <h2>🎥 直播列表</h2>
      <div class="header-actions">
        <button @click="startNewLive" class="btn btn-primary">
          🎬 开始新直播
        </button>
        <button @click="refreshList" class="btn btn-secondary">
          🔄 刷新
        </button>
      </div>
    </div>
    
    <div class="live-list-content">
      <!-- 正在直播的列表 -->
      <div v-if="liveStreams.length > 0" class="live-streams-section">
        <h3>正在直播 ({{ liveStreams.length }})</h3>
        <div class="streams-grid">
          <div 
            v-for="stream in liveStreams" 
            :key="stream.id"
            class="stream-card"
            @click="watchStream(stream)">
            <div class="stream-thumbnail">
              <img :src="stream.thumbnail" :alt="stream.title" v-if="stream.thumbnail">
              <div v-else class="thumbnail-placeholder">
                <div class="live-indicator">🔴 LIVE</div>
                <div class="placeholder-icon">📹</div>
              </div>
              <div class="stream-overlay">
                <div class="viewer-count">👥 {{ stream.viewerCount }}</div>
                <div class="live-badge">直播中</div>
              </div>
            </div>
            <div class="stream-info">
              <h4 class="stream-title">{{ stream.title }}</h4>
              <p class="stream-description">{{ stream.description }}</p>
              <div class="stream-meta">
                <span class="host-name">👤 {{ stream.hostName }}</span>
                <span class="duration">⏱ {{ formatDuration(stream.duration) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 没有直播时的提示 -->
      <div v-else class="no-live-streams">
        <div class="empty-state">
          <div class="empty-icon">📺</div>
          <h3>暂无直播</h3>
          <p>当前没有正在进行的直播</p>
          <button @click="startNewLive" class="btn btn-primary">
            🎬 成为第一个主播
          </button>
        </div>
      </div>
      
      <!-- 直播记录（已结束的直播） -->
      <div v-if="recordedStreams.length > 0" class="recorded-streams-section">
        <h3>直播回放 ({{ recordedStreams.length }})</h3>
        <div class="streams-grid">
          <div 
            v-for="stream in recordedStreams" 
            :key="stream.id"
            class="stream-card recorded"
            @click="watchRecording(stream)">
            <div class="stream-thumbnail">
              <img :src="stream.thumbnail" :alt="stream.title" v-if="stream.thumbnail">
              <div v-else class="thumbnail-placeholder">
                <div class="play-icon">▶️</div>
              </div>
              <div class="stream-overlay">
                <div class="duration">{{ formatDuration(stream.duration) }}</div>
              </div>
            </div>
            <div class="stream-info">
              <h4 class="stream-title">{{ stream.title }}</h4>
              <p class="stream-description">{{ stream.description }}</p>
              <div class="stream-meta">
                <span class="host-name">👤 {{ stream.hostName }}</span>
                <span class="record-date">📅 {{ formatDate(stream.endTime) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建新直播的模态框 -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>创建新直播</h3>
          <button @click="closeModal" class="close-btn">×</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label>直播标题 *</label>
            <input 
              v-model="newStream.title" 
              type="text" 
              placeholder="请输入直播标题"
              maxlength="50">
            <div class="char-count">{{ newStream.title.length }}/50</div>
          </div>
          
          <div class="form-group">
            <label>直播描述</label>
            <textarea 
              v-model="newStream.description" 
              placeholder="请输入直播描述（可选）"
              rows="3"
              maxlength="200"></textarea>
            <div class="char-count">{{ newStream.description.length }}/200</div>
          </div>
          
          <div class="form-group">
            <label>直播分类</label>
            <select v-model="newStream.category">
              <option value="entertainment">娱乐</option>
              <option value="gaming">游戏</option>
              <option value="education">教育</option>
              <option value="music">音乐</option>
              <option value="sports">体育</option>
              <option value="other">其他</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>直播设置</label>
            <div class="settings-options">
              <label class="checkbox-label">
                <input type="checkbox" v-model="newStream.record">
                录制直播
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="newStream.chatEnabled" checked>
                开启聊天室
              </label>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="closeModal" class="btn btn-secondary">取消</button>
          <button 
            @click="createStream" 
            class="btn btn-primary"
            :disabled="!newStream.title.trim()">
            🎬 开始直播
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LiveList',
  data() {
    return {
      // 直播列表数据
      liveStreams: [],
      recordedStreams: [],
      
      // 创建直播模态框
      showCreateModal: false,
      newStream: {
        title: '',
        description: '',
        category: 'entertainment',
        record: true,
        chatEnabled: true
      }
    }
  },
  mounted() {
    this.loadLiveStreams()
  },
  methods: {
    // 加载直播列表
    async loadLiveStreams() {
      try {
        // 模拟API调用获取直播数据
        await this.fetchLiveData()
      } catch (error) {
        console.error('加载直播列表失败:', error)
      }
    },
    
    // 模拟获取直播数据
    async fetchLiveData() {
      // 模拟API延迟
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 模拟直播数据
      this.liveStreams = [
        {
          id: '1',
          title: '深夜游戏直播 - 王者荣耀',
          description: '一起来打王者荣耀吧！',
          hostName: '游戏主播小明',
          viewerCount: 1250,
          duration: 3600, // 1小时
          thumbnail: '',
          category: 'gaming'
        },
        {
          id: '2',
          title: '音乐分享会',
          description: '分享好听的音乐给大家',
          hostName: '音乐达人',
          viewerCount: 890,
          duration: 1800, // 30分钟
          thumbnail: '',
          category: 'music'
        }
      ]
      
      // 模拟直播回放数据
      this.recordedStreams = [
        {
          id: 'r1',
          title: '昨天的游戏直播回放',
          description: '王者荣耀精彩对局',
          hostName: '游戏主播小明',
          duration: 7200, // 2小时
          endTime: Date.now() - 86400000, // 1天前
          thumbnail: '',
          category: 'gaming'
        }
      ]
    },
    
    // 刷新列表
    refreshList() {
      this.loadLiveStreams()
    },
    
    // 开始新直播
    startNewLive() {
      this.showCreateModal = true
      // 重置表单
      this.newStream = {
        title: '',
        description: '',
        category: 'entertainment',
        record: true,
        chatEnabled: true
      }
    },
    
    // 创建直播
    createStream() {
      if (!this.newStream.title.trim()) {
        alert('请输入直播标题')
        return
      }
      
      // 在实际项目中，这里会调用API创建直播
      console.log('创建直播:', this.newStream)
      
      // 跳转到直播推流页面（主播模式）
      this.$router.push({
        path: '/live/stream',
        query: { 
          title: this.newStream.title,
          description: this.newStream.description,
          category: this.newStream.category,
          quick: true
        }
      })
      
      this.closeModal()
    },
    
    // 观看直播
    watchStream(stream) {
      console.log('观看直播:', stream)
      // 跳转到直播观看页面
      this.$router.push({
        path: '/live/watch',
        query: { 
          streamId: stream.id,
          title: stream.title
        }
      })
    },
    
    // 观看回放
    watchRecording(stream) {
      console.log('观看回放:', stream)
      // 跳转到回放页面
      this.$router.push({
        path: '/live/recording',
        query: { 
          recordingId: stream.id,
          title: stream.title
        }
      })
    },
    
    // 关闭模态框
    closeModal() {
      this.showCreateModal = false
    },
    
    // 格式化时长
    formatDuration(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      
      if (hours > 0) {
        return `${hours}小时${minutes}分钟`
      } else {
        return `${minutes}分钟`
      }
    },
    
    // 格式化日期
    formatDate(timestamp) {
      return new Date(timestamp).toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
.live-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #1a1a1a;
  min-height: 100vh;
  color: white;
}

.live-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.live-list-header h2 {
  margin: 0;
  font-size: 28px;
  font-weight: bold;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-primary {
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
}

.live-streams-section,
.recorded-streams-section {
  margin-bottom: 40px;
}

.live-streams-section h3,
.recorded-streams-section h3 {
  margin-bottom: 20px;
  font-size: 20px;
  color: #ff6b6b;
}

.streams-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.stream-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stream-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 107, 107, 0.3);
}

.stream-card.recorded {
  opacity: 0.8;
}

.stream-card.recorded:hover {
  opacity: 1;
}

.stream-thumbnail {
  position: relative;
  height: 180px;
  background: #2a2a2a;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.stream-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
}

.live-indicator {
  position: absolute;
  top: 10px;
  left: 10px;
  background: #ff4757;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  animation: pulse 2s infinite;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.play-icon {
  font-size: 48px;
}

.stream-overlay {
  position: absolute;
  bottom: 10px;
  left: 10px;
  right: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.viewer-count,
.duration,
.live-badge {
  background: rgba(0, 0, 0, 0.7);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.live-badge {
  background: #ff4757;
  color: white;
}

.stream-info {
  padding: 15px;
}

.stream-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: bold;
  line-height: 1.3;
}

.stream-description {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.stream-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.no-live-streams {
  text-align: center;
  padding: 60px 20px;
}

.empty-state {
  max-width: 400px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

.empty-state p {
  margin: 0 0 20px 0;
  color: rgba(255, 255, 255, 0.7);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: #2a2a2a;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 5px;
}

.settings-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-label input {
  width: auto;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .live-list-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .streams-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>