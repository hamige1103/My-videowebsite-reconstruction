// 导入axios实例
import httpRequest from '../request/index'

// 智能搜索API
const smartSearchAPI = {
  // 执行智能搜索
  search(question) {
    return httpRequest({
      url: '/v1/smart-search',
      method: 'post',
      data: { question }
    })
  },
  
  // 执行千问智能搜索
  qianwenSearch(question) {
    return httpRequest({
      url: '/v1/qianwen-search',
      method: 'post',
      data: { question }
    })
  },
  
  // 检查千问API健康状态
  checkQianwenHealth() {
    return httpRequest({
      url: '/v1/qianwen-search/health',
      method: 'get'
    })
  },
  
  // 获取搜索示例
  getExamples() {
    return httpRequest({
      url: '/v1/smart-search/examples',
      method: 'get'
    })
  }
}

export default smartSearchAPI