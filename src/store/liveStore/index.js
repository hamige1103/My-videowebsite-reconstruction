// 直播状态管理模块
import { defineStore } from 'pinia'
import * as liveApi from '../../apis/live.js'

export const useLiveStore = defineStore('live', {
  state: () => ({
    // 直播列表
    liveList: [],
    hotLives: [],
    recommendedLives: [],
    
    // 当前直播信息
    currentLive: null,
    currentStreamUrl: '',
    currentPlayUrl: '',
    
    // 直播状态
    isStreaming: false,
    isWatching: false,
    streamStatus: 'idle', // idle, connecting, live, error, ended
    
    // 聊天室
    chatMessages: [],
    isChatConnected: false,
    
    // 观众统计
    viewerCount: 0,
    likeCount: 0,
    shareCount: 0,
    
    // 播放器状态
    isPlaying: false,
    isMuted: false,
    volume: 1,
    isFullscreen: false,
    
    // 错误信息
    error: null,
    
    // 加载状态
    loading: {
      liveList: false,
      liveDetail: false,
      stream: false
    }
  }),

  getters: {
    // 获取正在直播的列表
    activeLives: (state) => {
      return state.liveList.filter(live => live.status === 'live')
    },
    
    // 获取即将开始的直播
    upcomingLives: (state) => {
      return state.liveList.filter(live => live.status === 'scheduled')
    },
    
    // 获取已结束的直播
    endedLives: (state) => {
      return state.liveList.filter(live => live.status === 'ended')
    },
    
    // 获取当前直播信息
    currentLiveInfo: (state) => {
      return state.currentLive
    },
    
    // 获取聊天室状态
    chatStatus: (state) => {
      return {
        connected: state.isChatConnected,
        messageCount: state.chatMessages.length,
        lastMessage: state.chatMessages[state.chatMessages.length - 1]
      }
    },
    
    // 获取直播统计
    liveStats: (state) => {
      return {
        viewerCount: state.viewerCount,
        likeCount: state.likeCount,
        shareCount: state.shareCount,
        duration: state.currentLive?.duration || 0
      }
    }
  },

  actions: {
    // 获取直播列表
    async fetchLiveList(params = {}) {
      this.loading.liveList = true
      try {
        const response = await liveApi.getLiveList(params)
        this.liveList = response.data || []
        return response.data
      } catch (error) {
        this.error = '获取直播列表失败'
        console.error('获取直播列表失败:', error)
        throw error
      } finally {
        this.loading.liveList = false
      }
    },

    // 获取热门直播
    async fetchHotLives() {
      try {
        const response = await liveApi.getHotLives()
        this.hotLives = response.data || []
        return response.data
      } catch (error) {
        console.error('获取热门直播失败:', error)
        throw error
      }
    },

    // 获取推荐直播
    async fetchRecommendedLives() {
      try {
        const response = await liveApi.getRecommendedLives()
        this.recommendedLives = response.data || []
        return response.data
      } catch (error) {
        console.error('获取推荐直播失败:', error)
        throw error
      }
    },

    // 获取直播详情
    async fetchLiveDetail(liveId) {
      this.loading.liveDetail = true
      try {
        const response = await liveApi.getLiveDetail(liveId)
        this.currentLive = response.data
        return response.data
      } catch (error) {
        this.error = '获取直播详情失败'
        console.error('获取直播详情失败:', error)
        throw error
      } finally {
        this.loading.liveDetail = false
      }
    },

    // 创建直播
    async createLive(liveData) {
      try {
        const response = await liveApi.createLive(liveData)
        this.currentLive = response.data
        return response.data
      } catch (error) {
        this.error = '创建直播失败'
        console.error('创建直播失败:', error)
        throw error
      }
    },

    // 开始直播
    async startLive(liveId) {
      this.loading.stream = true
      this.streamStatus = 'connecting'
      try {
        const response = await liveApi.startLive(liveId)
        const streamUrl = await liveApi.getStreamUrl(liveId)
        
        this.currentStreamUrl = streamUrl.data
        this.isStreaming = true
        this.streamStatus = 'live'
        
        return response.data
      } catch (error) {
        this.streamStatus = 'error'
        this.error = '开始直播失败'
        console.error('开始直播失败:', error)
        throw error
      } finally {
        this.loading.stream = false
      }
    },

    // 停止直播
    async stopLive(liveId) {
      try {
        const response = await liveApi.stopLive(liveId)
        
        this.isStreaming = false
        this.streamStatus = 'ended'
        this.currentStreamUrl = ''
        
        return response.data
      } catch (error) {
        this.error = '停止直播失败'
        console.error('停止直播失败:', error)
        throw error
      }
    },

    // 观看直播
    async watchLive(liveId) {
      this.loading.stream = true
      this.streamStatus = 'connecting'
      try {
        const playUrl = await liveApi.getPlayUrl(liveId)
        
        this.currentPlayUrl = playUrl.data
        this.isWatching = true
        this.streamStatus = 'live'
        
        // 获取聊天记录
        await this.fetchChatHistory(liveId)
        
        return playUrl.data
      } catch (error) {
        this.streamStatus = 'error'
        this.error = '连接直播失败'
        console.error('连接直播失败:', error)
        throw error
      } finally {
        this.loading.stream = false
      }
    },

    // 发送聊天消息
    async sendChatMessage(liveId, message) {
      try {
        const response = await liveApi.sendChatMessage(liveId, message)
        
        // 添加到本地消息列表
        this.chatMessages.push({
          id: Date.now(),
          type: 'user',
          sender: '我',
          time: new Date().toLocaleTimeString('zh-CN'),
          text: message
        })
        
        return response.data
      } catch (error) {
        console.error('发送消息失败:', error)
        throw error
      }
    },

    // 获取聊天记录
    async fetchChatHistory(liveId) {
      try {
        const response = await liveApi.getChatHistory(liveId)
        this.chatMessages = response.data || []
        this.isChatConnected = true
        return response.data
      } catch (error) {
        console.error('获取聊天记录失败:', error)
        throw error
      }
    },

    // 发送礼物
    async sendGift(liveId, giftId) {
      try {
        const response = await liveApi.sendGift(liveId, giftId)
        
        // 添加到本地消息列表
        this.chatMessages.push({
          id: Date.now(),
          type: 'gift',
          sender: '我',
          time: new Date().toLocaleTimeString('zh-CN'),
          text: '送出了礼物',
          giftId: giftId
        })
        
        return response.data
      } catch (error) {
        console.error('发送礼物失败:', error)
        throw error
      }
    },

    // 点赞直播
    async likeLive(liveId) {
      try {
        const response = await liveApi.likeLive(liveId)
        this.likeCount += 1
        return response.data
      } catch (error) {
        console.error('点赞失败:', error)
        throw error
      }
    },

    // 分享直播
    async shareLive(liveId) {
      try {
        const response = await liveApi.shareLive(liveId)
        this.shareCount += 1
        return response.data
      } catch (error) {
        console.error('分享失败:', error)
        throw error
      }
    },

    // 获取直播统计
    async fetchLiveStats(liveId) {
      try {
        const response = await liveApi.getLiveStats(liveId)
        const stats = response.data
        
        if (stats) {
          this.viewerCount = stats.viewerCount || 0
          this.likeCount = stats.likeCount || 0
          this.shareCount = stats.shareCount || 0
        }
        
        return stats
      } catch (error) {
        console.error('获取直播统计失败:', error)
        throw error
      }
    },

    // 关注主播
    async followHost(hostId) {
      try {
        const response = await liveApi.followHost(hostId)
        return response.data
      } catch (error) {
        console.error('关注主播失败:', error)
        throw error
      }
    },

    // 取消关注主播
    async unfollowHost(hostId) {
      try {
        const response = await liveApi.unfollowHost(hostId)
        return response.data
      } catch (error) {
        console.error('取消关注失败:', error)
        throw error
      }
    },

    // 搜索直播
    async searchLives(keyword) {
      try {
        const response = await liveApi.searchLives(keyword)
        return response.data
      } catch (error) {
        console.error('搜索直播失败:', error)
        throw error
      }
    },

    // 设置播放状态
    setPlayState(playing) {
      this.isPlaying = playing
    },

    // 设置静音状态
    setMuteState(muted) {
      this.isMuted = muted
    },

    // 设置音量
    setVolume(volume) {
      this.volume = volume
    },

    // 设置全屏状态
    setFullscreenState(fullscreen) {
      this.isFullscreen = fullscreen
    },

    // 添加系统消息
    addSystemMessage(text) {
      this.chatMessages.push({
        id: Date.now(),
        type: 'system',
        sender: '系统',
        time: new Date().toLocaleTimeString('zh-CN'),
        text: text
      })
    },

    // 清空错误
    clearError() {
      this.error = null
    },

    // 重置直播状态
    resetLiveState() {
      this.currentLive = null
      this.currentStreamUrl = ''
      this.currentPlayUrl = ''
      this.isStreaming = false
      this.isWatching = false
      this.streamStatus = 'idle'
      this.chatMessages = []
      this.isChatConnected = false
      this.viewerCount = 0
      this.likeCount = 0
      this.shareCount = 0
      this.isPlaying = false
      this.isMuted = false
      this.volume = 1
      this.isFullscreen = false
      this.error = null
    }
  }
})