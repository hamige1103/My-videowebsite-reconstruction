import axios from 'axios'
import { localGet } from '../utils'

// 创建一个 axios 实例
const service = axios.create({
	baseURL: 'http://localhost:8000/api', // 连接到FastAPI后端
	timeout: 60000, // 请求超时时间毫秒
	withCredentials: true, // 异步请求携带cookie
	headers: {
		// 设置后端需要的传参类型
		'Content-Type': 'application/json',
		'X-Requested-With': 'XMLHttpRequest',
	},
})

// 添加请求拦截器
service.interceptors.request.use(
	function (config) {
		// 在发送请求之前动态获取token
		const token = localGet('token')
		if (token) {
			// 所有接口统一使用Bearer格式，因为收藏接口使用的是flask_auth依赖
			if (token.startsWith('jwt ')) {
				// 将jwt前缀转换为Bearer前缀
				const token_without_prefix = token.replace('jwt ', '')
				config.headers.Authorization = `Bearer ${token_without_prefix}`
			} else if (!token.startsWith('Bearer ')) {
				config.headers.Authorization = `Bearer ${token}`
			} else {
				config.headers.Authorization = token
			}
		}
		return config
	},
	function (error) {
		// 对请求错误做些什么
		console.log(error)
		return Promise.reject(error)
	}
)

// 添加响应拦截器
service.interceptors.response.use(
	function (response) {
		// console.log(response)
		// 2xx 范围内的状态码都会触发该函数。
		// 对响应数据做点什么
		// 直接返回完整的响应对象，让前端组件可以访问 response.data
		return response
	},
	function (error) {
		// 超出 2xx 范围的状态码都会触发该函数。
		// 对响应错误做点什么
		console.log(error)
		return Promise.reject(error)
	}
)

export default service

