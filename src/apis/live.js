// 直播相关API接口
import request from '../request/index.js'

// 获取直播列表
export const getLiveList = (params = {}) => {
  return request({
    url: '/v1/live/list',
    method: 'GET',
    params
  })
}

// 创建直播
export const createLive = (data) => {
  return request({
    url: '/v1/live/create',
    method: 'POST',
    data
  })
}

// 获取直播详情
export const getLiveDetail = (liveId) => {
  return request({
    url: `/v1/live/detail/${liveId}`,
    method: 'GET'
  })
}

// 开始直播
export const startLive = (liveId) => {
  return request({
    url: `/v1/live/start/${liveId}`,
    method: 'POST'
  })
}

// 停止直播
export const stopLive = (liveId) => {
  return request({
    url: `/v1/live/stop/${liveId}`,
    method: 'POST'
  })
}

// 获取直播推流地址
export const getStreamUrl = (liveId) => {
  return request({
    url: `/v1/live/stream/${liveId}`,
    method: 'GET'
  })
}

// 获取直播播放地址
export const getPlayUrl = (liveId) => {
  return request({
    url: `/v1/live/play/${liveId}`,
    method: 'GET'
  })
}

// 发送聊天消息
export const sendChatMessage = (liveId, message) => {
  return request({
    url: `/v1/live/chat/${liveId}`,
    method: 'POST',
    data: { message }
  })
}

// 获取聊天记录
export const getChatHistory = (liveId) => {
  return request({
    url: `/v1/live/chat/${liveId}`,
    method: 'GET'
  })
}

// 发送礼物
export const sendGift = (liveId, giftId) => {
  return request({
    url: `/v1/live/gift/${liveId}`,
    method: 'POST',
    data: { giftId }
  })
}

// 获取礼物列表
export const getGiftList = () => {
  return request({
    url: '/v1/live/gifts',
    method: 'GET'
  })
}

// 点赞直播
export const likeLive = (liveId) => {
  return request({
    url: `/v1/live/like/${liveId}`,
    method: 'POST'
  })
}

// 分享直播
export const shareLive = (liveId) => {
  return request({
    url: `/v1/live/share/${liveId}`,
    method: 'POST'
  })
}

// 获取直播统计数据
export const getLiveStats = (liveId) => {
  return request({
    url: `/v1/live/stats/${liveId}`,
    method: 'GET'
  })
}

// 获取热门直播
export const getHotLives = () => {
  return request({
    url: '/v1/live/hot',
    method: 'GET'
  })
}

// 获取推荐直播
export const getRecommendedLives = () => {
  return request({
    url: '/v1/live/recommended',
    method: 'GET'
  })
}

// 关注主播
export const followHost = (hostId) => {
  return request({
    url: `/v1/live/follow/${hostId}`,
    method: 'POST'
  })
}

// 取消关注主播
export const unfollowHost = (hostId) => {
  return request({
    url: `/v1/live/unfollow/${hostId}`,
    method: 'POST'
  })
}

// 获取主播信息
export const getHostInfo = (hostId) => {
  return request({
    url: `/v1/live/host/${hostId}`,
    method: 'GET'
  })
}

// 举报直播
export const reportLive = (liveId, reason) => {
  return request({
    url: `/v1/live/report/${liveId}`,
    method: 'POST',
    data: { reason }
  })
}

// 获取直播分类
export const getLiveCategories = () => {
  return request({
    url: '/v1/live/categories',
    method: 'GET'
  })
}

// 搜索直播
export const searchLives = (keyword) => {
  return request({
    url: '/v1/live/search',
    method: 'GET',
    params: { keyword }
  })
}

// 获取我的直播记录
export const getMyLives = () => {
  return request({
    url: '/v1/live/my-lives',
    method: 'GET'
  })
}

// 删除直播记录
export const deleteLive = (liveId) => {
  return request({
    url: `/v1/live/delete/${liveId}`,
    method: 'DELETE'
  })
}

// ========== 直播带货相关API ==========

// 添加直播商品
export const addLiveProduct = (liveId, productData) => {
  return request({
    url: `/v1/live/commerce/${liveId}/products`,
    method: 'POST',
    data: productData
  })
}

// 获取直播商品列表
export const getLiveProducts = (liveId) => {
  return request({
    url: `/v1/live/commerce/${liveId}/products`,
    method: 'GET'
  })
}

// 更新直播商品
export const updateLiveProduct = (liveId, productId, productData) => {
  return request({
    url: `/v1/live/commerce/${liveId}/products/${productId}`,
    method: 'PUT',
    data: productData
  })
}

// 删除直播商品
export const removeLiveProduct = (liveId, productId) => {
  return request({
    url: `/v1/live/commerce/${liveId}/products/${productId}`,
    method: 'DELETE'
  })
}

// 创建直播带货订单
export const createLiveOrder = (liveId, orderData) => {
  return request({
    url: `/v1/live/commerce/${liveId}/orders`,
    method: 'POST',
    data: orderData
  })
}

// 获取直播订单列表（主播端）
export const getLiveOrders = (liveId) => {
  return request({
    url: `/v1/live/commerce/${liveId}/orders`,
    method: 'GET'
  })
}

// 获取直播带货统计数据
export const getLiveCommerceStats = (liveId) => {
  return request({
    url: `/v1/live/commerce/${liveId}/stats/commerce`,
    method: 'GET'
  })
}

// 推广直播商品
export const promoteLiveProduct = (liveId, productId) => {
  return request({
    url: `/v1/live/commerce/${liveId}/promote/${productId}`,
    method: 'POST'
  })
}

// 设置直播封面
export const setLiveCover = (liveId, coverUrl) => {
  return request({
    url: `/v1/live/cover/${liveId}`,
    method: 'POST',
    data: { coverUrl }
  })
}

// 设置直播标题
export const setLiveTitle = (liveId, title) => {
  return request({
    url: `/v1/live/title/${liveId}`,
    method: 'POST',
    data: { title }
  })
}

// 设置直播分类
export const setLiveCategory = (liveId, category) => {
  return request({
    url: `/v1/live/category/${liveId}`,
    method: 'POST',
    data: { category }
  })
}

// 设置直播隐私
export const setLivePrivacy = (liveId, isPrivate) => {
  return request({
    url: `/v1/live/privacy/${liveId}`,
    method: 'POST',
    data: { isPrivate }
  })
}

// 获取直播录制列表
export const getLiveRecordings = (liveId) => {
  return request({
    url: `/v1/live/recordings/${liveId}`,
    method: 'GET'
  })
}

// 下载直播录制
export const downloadRecording = (recordingId) => {
  return request({
    url: `/v1/live/download/${recordingId}`,
    method: 'GET'
  })
}