// 获取视频播放地址
import httpRequest from '../request/index'

export function getVideoPlay(video_id) {
    return httpRequest({
        url: `/v1/video/play/${video_id}`,
        method: 'get',
    })
}