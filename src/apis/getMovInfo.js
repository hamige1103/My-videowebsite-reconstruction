// 导入axios实例
import httpRequest from '../request/index'

// 获取视频列表
export default function getMovInfo(params) {
	return httpRequest({
		url: '/v1/video/list',
		method: 'get',
		params: params,
	})
}
