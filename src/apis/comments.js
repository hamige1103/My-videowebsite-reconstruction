// 导入axios实例
import httpRequest from '../request/index'

// 发布评论
export function publishComment(data) {
	return httpRequest({
		url: '/v1/comment/create',
		method: 'post',
		data: data,
	})
}

// 获取评论列表
export function showVodComment(params) {
	return httpRequest({
		url: '/v1/comment/list',
		method: 'get',
		params: params,
	})
}

// 回复评论
export function replyCommentPost(data) {
	return httpRequest({
		url: '/v1/comment/create',
		method: 'post',
		data: data,
	})
}