// 导入axios实例
import httpRequest from '../request/index'

// 获取收藏列表
export function getCollectionList() {
	return httpRequest({
		url: '/v1/collection/list',
		method: 'get',
	})
}

// 添加收藏
export function addCollection(data) {
	return httpRequest({
		url: '/v1/collection/add',
		method: 'post',
		data: data,
	})
}

// 删除收藏
export function removeCollection(data) {
	return httpRequest({
		url: '/v1/collection/remove',
		method: 'delete',
		data: data,
	})
}

// 检查是否收藏
export function checkCollection(params) {
	return httpRequest({
		url: `/v1/collection/check/${params.video_id}`,
		method: 'get',
	})
}

// 获取收藏列表
export function getCollectionListByPage(params) {
	return httpRequest({
		url: '/v1/collection/list',
		method: 'get',
		params: params,
	})
}