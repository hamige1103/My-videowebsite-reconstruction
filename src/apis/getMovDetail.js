// 导入axios实例
import httpRequest from '../request/index'

// 获取视频详情
export default function getMovDetail(param) {
	return httpRequest({
		url: `/v1/video/detail/${param.vod_id}`,
		method: 'get',
	})
}
