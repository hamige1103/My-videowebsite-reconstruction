<template>
  <div class="live-stream-container">
    <!-- 直播带货功能区域 -->
    <div class="live-commerce-section" v-if="!isHost">
      <!-- 商品展示和购物车切换标签 -->
      <div class="commerce-tabs">
        <button 
          @click="activeTab = 'products'"
          :class="{ active: activeTab === 'products' }"
          class="tab-btn">
          🛍️ 商品列表
        </button>
        <button 
          @click="activeTab = 'cart'"
          :class="{ active: activeTab === 'cart' }"
          class="tab-btn">
          🛒 购物车
        </button>
      </div>
      
      <!-- 商品列表 -->
      <LiveProductList 
        v-if="activeTab === 'products'"
        :live-id="parseInt(streamId)"
        @add-to-cart="handleAddToCart"
        class="product-list-component" />
      
      <!-- 购物车 -->
      <LiveCart 
        v-if="activeTab === 'cart'"
        :live-id="parseInt(streamId)"
        @order-created="handleOrderCreated"
        class="cart-component" />
    </div>
    
    <!-- 直播控制面板 -->
    <div class="live-control-panel" v-if="isHost">
      <div class="panel-header">
        <h3>直播控制台</h3>
        <div class="status-indicator" :class="{ active: isStreaming }">
          {{ isStreaming ? '直播中' : '未开始' }}
        </div>
      </div>
      
      <div class="control-buttons">
        <button 
          v-if="!isStreaming" 
          @click="startStream" 
          class="btn btn-primary"
          :disabled="!isReady">
          🎥 开始直播
        </button>
        <button 
          v-else 
          @click="stopStream" 
          class="btn btn-danger">
          ⏹ 停止直播
        </button>
        
        <button @click="toggleSettings" class="btn btn-secondary">
          ⚙️ 设置
        </button>
        
        <!-- 商品管理按钮 -->
        <button @click="showProductManager" class="btn btn-success">
          🛍️ 商品管理
        </button>
      </div>
      
      <!-- 直播设置面板 -->
      <div v-if="showSettings" class="settings-panel">
        <div class="setting-item">
          <label>直播标题：</label>
          <input v-model="streamTitle" type="text" placeholder="请输入直播标题">
        </div>
        <div class="setting-item">
          <label>直播描述：</label>
          <textarea v-model="streamDescription" placeholder="请输入直播描述"></textarea>
        </div>
        <div class="setting-item">
          <label>视频质量：</label>
          <select v-model="videoQuality">
            <option value="720p">720p</option>
            <option value="1080p">1080p</option>
            <option value="480p">480p</option>
          </select>
        </div>
        <div class="setting-item">
          <label>是否录制：</label>
          <input type="checkbox" v-model="recordStream">
        </div>
      </div>
    </div>
    
    <!-- 直播视频区域 -->
    <div class="live-video-area">
      <!-- 主播端：摄像头预览和推流 -->
      <div v-if="isHost" class="host-view">
        <video 
          ref="localVideo" 
          class="local-video" 
          autoplay 
          muted
          v-show="isStreaming || isPreviewing">
        </video>
        <div v-if="!isPreviewing && !isStreaming" class="preview-placeholder">
          <div class="placeholder-content">
            <div class="camera-icon">📹</div>
            <p>点击"开始直播"开始推流</p>
          </div>
        </div>
        
        <!-- 直播信息显示 -->
        <div v-if="isStreaming" class="stream-info">
          <div class="viewer-count">👥 {{ viewerCount }} 人观看</div>
          <div class="stream-title">{{ streamTitle }}</div>
          <div class="live-duration">⏱ {{ formatDuration(liveDuration) }}</div>
        </div>
      </div>
      
      <!-- 观众端：观看直播 -->
      <div v-else class="audience-view">
        <VideoPlay 
          v-if="currentStreamUrl" 
          :src="currentStreamUrl" 
          :type="'application/x-mpegURL'"
          :poster="streamThumbnail"
          @error="handleStreamError"
          class="stream-player"/>
        
        <div v-if="!currentStreamUrl" class="no-stream">
          <div class="no-stream-content">
            <div class="offline-icon">📺</div>
            <h3>直播未开始</h3>
            <p>主播尚未开始直播，请稍后再来</p>
          </div>
        </div>
        
        <!-- 直播信息 -->
        <div v-if="currentStreamUrl" class="stream-info-audience">
          <h2>{{ streamTitle }}</h2>
          <p>{{ streamDescription }}</p>
          <div class="stream-stats">
            <span>👥 {{ viewerCount }} 人观看</span>
            <span>⏱ {{ formatDuration(liveDuration) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 聊天室 -->
    <div class="live-chat" v-if="showChat">
      <div class="chat-header">
        <h4>聊天室</h4>
        <span class="online-count">在线: {{ onlineUsers }}</span>
      </div>
      
      <div class="chat-messages" ref="chatMessages">
        <div 
          v-for="message in chatMessages" 
          :key="message.id"
          :class="['message', { 'own-message': message.isOwn }]">
          <div class="message-header">
            <span class="username">{{ message.username }}</span>
            <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
          </div>
          <div class="message-content">{{ message.content }}</div>
        </div>
      </div>
      
      <div class="chat-input">
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage"
          placeholder="输入消息..."
          :disabled="!isConnected">
        <button @click="sendMessage" :disabled="!isConnected || !newMessage.trim()">
          发送
        </button>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-overlay">
      <div class="error-content">
        <div class="error-icon">❌</div>
        <h3>直播错误</h3>
        <p>{{ errorMessage }}</p>
        <button @click="clearError" class="btn btn-primary">确定</button>
      </div>
    </div>
    
    <!-- 商品管理弹窗 -->
    <div v-if="showProductManagerDialog" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>商品管理</h3>
          <button @click="closeProductManager" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <LiveProductManager :live-id="parseInt(streamId)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VideoPlay from './VideoPlay.vue'
import LiveProductList from './LiveProductList.vue'
import LiveCart from './LiveCart.vue'
import LiveProductManager from './LiveProductManager.vue'

export default {
  name: 'LiveStream',
  components: {
    VideoPlay,
    LiveProductList,
    LiveCart,
    LiveProductManager
  },
  props: {
    isHost: {
      type: Boolean,
      default: false
    },
    streamId: {
      type: String,
      default: ''
    },
    showChat: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      // 直播带货相关状态
      activeTab: 'products',
      showProductManagerDialog: false,
      
      // 直播状态
      isStreaming: false,
      isPreviewing: false,
      isReady: false,
      
      // 直播设置
      showSettings: false,
      streamTitle: '我的直播',
      streamDescription: '',
      videoQuality: '720p',
      recordStream: true,
      
      // 直播数据
      viewerCount: 0,
      liveDuration: 0,
      currentStreamUrl: '',
      streamThumbnail: '',
      
      // 聊天室
      chatMessages: [],
      newMessage: '',
      onlineUsers: 0,
      isConnected: false,
      
      // 错误处理
      error: false,
      errorMessage: '',
      
      // 媒体流和定时器
      localStream: null,
      streamInterval: null,
      durationInterval: null
    }
  },
  mounted() {
    this.initializeStream()
    if (this.isHost) {
      this.setupMediaDevices()
    } else {
      this.connectToStream()
    }
  },
  beforeUnmount() {
    this.cleanup()
  },
  methods: {
    // 直播带货相关方法
    handleAddToCart(product) {
      console.log('添加到购物车:', product)
      // 这里会触发购物车组件的添加事件
    },
    
    handleOrderCreated(order) {
      console.log('订单创建成功:', order)
      this.$message.success('订单创建成功！')
    },
    
    showProductManager() {
      this.showProductManagerDialog = true
    },
    
    closeProductManager() {
      this.showProductManagerDialog = false
    },
    
    // 初始化直播
    initializeStream() {
      console.log('初始化直播功能')
      this.isReady = true
    },
    
    // 设置媒体设备（主播端）
    async setupMediaDevices() {
      try {
        // 检查媒体设备权限
        const devices = await navigator.mediaDevices.enumerateDevices()
        const videoDevices = devices.filter(device => device.kind === 'videoinput')
        
        if (videoDevices.length === 0) {
          throw new Error('未检测到摄像头设备')
        }
        
        console.log('找到摄像头设备:', videoDevices)
        this.isReady = true
        
      } catch (error) {
        console.error('设备检测失败:', error)
        this.showError('摄像头检测失败: ' + error.message)
      }
    },
    
    // 开始直播
    async startStream() {
      try {
        this.isPreviewing = true
        
        // 获取摄像头和麦克风权限
        const constraints = {
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            frameRate: { ideal: 30 }
          },
          audio: true
        }
        
        this.localStream = await navigator.mediaDevices.getUserMedia(constraints)
        
        // 显示本地视频预览
        const video = this.$refs.localVideo
        if (video) {
          video.srcObject = this.localStream
        }
        
        // 模拟推流到服务器（实际项目中需要真实的推流服务器）
        await this.startStreamingToServer()
        
        this.isStreaming = true
        this.isPreviewing = false
        this.liveDuration = 0
        
        // 开始计时
        this.durationInterval = setInterval(() => {
          this.liveDuration++
        }, 1000)
        
        // 模拟观众数量变化
        this.startViewerSimulation()
        
        console.log('直播开始成功')
        
      } catch (error) {
        console.error('开始直播失败:', error)
        this.showError('开始直播失败: ' + error.message)
        this.isPreviewing = false
      }
    },
    
    // 模拟推流到服务器
    async startStreamingToServer() {
      // 在实际项目中，这里需要连接到真实的流媒体服务器
      // 如使用 WebRTC、RTMP 或 HLS 推流
      return new Promise((resolve) => {
        setTimeout(() => {
          // 生成模拟的直播流URL
          this.currentStreamUrl = `/api/live/stream/${Date.now()}.m3u8`
          resolve()
        }, 1000)
      })
    },
    
    // 停止直播
    async stopStream() {
      try {
        this.isStreaming = false
        this.isPreviewing = false
        
        // 停止本地流
        if (this.localStream) {
          this.localStream.getTracks().forEach(track => track.stop())
          this.localStream = null
        }
        
        // 清理定时器
        if (this.streamInterval) {
          clearInterval(this.streamInterval)
          this.streamInterval = null
        }
        
        if (this.durationInterval) {
          clearInterval(this.durationInterval)
          this.durationInterval = null
        }
        
        // 停止推流
        await this.stopStreamingFromServer()
        
        console.log('直播已停止')
        
      } catch (error) {
        console.error('停止直播失败:', error)
        this.showError('停止直播失败: ' + error.message)
      }
    },
    
    // 模拟停止推流
    async stopStreamingFromServer() {
      return new Promise((resolve) => {
        setTimeout(() => {
          this.currentStreamUrl = ''
          resolve()
        }, 500)
      })
    },
    
    // 连接直播流（观众端）
    async connectToStream() {
      try {
        // 在实际项目中，这里需要从服务器获取直播流URL
        // 模拟连接直播流
        this.currentStreamUrl = this.isHost ? '' : '/api/live/stream/demo.m3u8'
        
        // 模拟连接聊天室
        this.connectToChat()
        
        // 模拟观众数量
        this.startViewerSimulation()
        
      } catch (error) {
        console.error('连接直播失败:', error)
        this.showError('连接直播失败: ' + error.message)
      }
    },
    
    // 模拟观众数量变化
    startViewerSimulation() {
      this.streamInterval = setInterval(() => {
        if (this.isStreaming || this.currentStreamUrl) {
          // 随机增减观众数量
          const change = Math.random() > 0.5 ? 1 : -1
          this.viewerCount = Math.max(0, this.viewerCount + change)
          
          // 在线用户数（观众数 + 主播）
          this.onlineUsers = this.viewerCount + (this.isStreaming ? 1 : 0)
        }
      }, 3000)
    },
    
    // 连接聊天室
    connectToChat() {
      // 模拟聊天室连接
      this.isConnected = true
      
      // 添加一些模拟消息
      this.chatMessages = [
        {
          id: 1,
          username: '系统',
          content: '欢迎来到直播间！',
          timestamp: Date.now() - 60000,
          isOwn: false
        }
      ]
    },
    
    // 发送消息
    sendMessage() {
      if (!this.newMessage.trim()) return
      
      const message = {
        id: Date.now(),
        username: this.isHost ? '主播' : '观众',
        content: this.newMessage,
        timestamp: Date.now(),
        isOwn: true
      }
      
      this.chatMessages.push(message)
      this.newMessage = ''
      
      // 滚动到最新消息
      this.$nextTick(() => {
        const container = this.$refs.chatMessages
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },
    
    // 切换设置面板
    toggleSettings() {
      this.showSettings = !this.showSettings
    },
    
    // 处理流错误
    handleStreamError() {
      if (this.isHost) {
        this.showError('推流失败，请检查网络连接')
      } else {
        this.showError('观看直播失败，请刷新重试')
      }
    },
    
    // 显示错误
    showError(message) {
      this.error = true
      this.errorMessage = message
    },
    
    // 清除错误
    clearError() {
      this.error = false
      this.errorMessage = ''
    },
    
    // 格式化时间
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    
    // 格式化时长
    formatDuration(seconds) {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60
      
      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
      } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      }
    },
    
    // 清理资源
    cleanup() {
      if (this.localStream) {
        this.localStream.getTracks().forEach(track => track.stop())
      }
      
      if (this.streamInterval) {
        clearInterval(this.streamInterval)
      }
      
      if (this.durationInterval) {
        clearInterval(this.durationInterval)
      }
    }
  }
}
</script>

<style scoped>
.live-stream-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a1a;
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* 直播带货功能区域样式 */
.live-commerce-section {
  width: 350px;
  background: rgba(0, 0, 0, 0.8);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(10px);
}

.commerce-tabs {
  display: flex;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.tab-btn.active {
  color: #ff6b6b;
  border-bottom-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
}

.product-list-component,
.cart-component {
  flex: 1;
  overflow-y: auto;
}

/* 商品管理弹窗样式 */
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
  z-index: 2000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #e9ecef;
  color: #333;
}

.modal-body {
  padding: 0;
  max-height: calc(90vh - 80px);
  overflow-y: auto;
}

.live-control-panel {
  background: rgba(0, 0, 0, 0.8);
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.status-indicator {
  padding: 5px 10px;
  border-radius: 15px;
  background: #666;
  font-size: 12px;
}

.status-indicator.active {
  background: #ff4757;
  animation: pulse 2s infinite;
}

.control-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #ff6b6b, #ffa726);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #ff4757, #ff6b6b);
  color: white;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.settings-panel {
  margin-top: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.setting-item {
  margin-bottom: 10px;
}

.setting-item label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
}

.setting-item input,
.setting-item textarea,
.setting-item select {
  width: 100%;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.live-video-area {
  flex: 1;
  display: flex;
  position: relative;
}

.host-view, .audience-view {
  flex: 1;
  position: relative;
  background: #000;
}

.local-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
}

.placeholder-content {
  text-align: center;
}

.camera-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.stream-info {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.7);
  padding: 10px 15px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.viewer-count, .live-duration {
  font-size: 14px;
  margin-bottom: 5px;
}

.stream-title {
  font-weight: bold;
  font-size: 16px;
}

.no-stream {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-stream-content {
  text-align: center;
}

.offline-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.stream-info-audience {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.8);
  padding: 15px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.stream-stats {
  display: flex;
  gap: 15px;
  margin-top: 10px;
  font-size: 14px;
}

.live-chat {
  width: 300px;
  background: rgba(0, 0, 0, 0.8);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  max-height: 400px;
}

.message {
  margin-bottom: 15px;
  padding: 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
}

.message.own-message {
  background: rgba(255, 107, 107, 0.2);
  margin-left: 20px;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 12px;
  opacity: 0.7;
}

.message-content {
  font-size: 14px;
  line-height: 1.4;
}

.chat-input {
  padding: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 10px;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.chat-input button {
  padding: 10px 15px;
  background: #ff6b6b;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
}

.error-overlay {
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
}

.error-content {
  background: white;
  padding: 30px;
  border-radius: 10px;
  text-align: center;
  color: #333;
  max-width: 400px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .live-stream-container {
    flex-direction: column;
  }
  
  .live-chat {
    width: 100%;
    height: 200px;
  }
  
  .control-buttons {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>