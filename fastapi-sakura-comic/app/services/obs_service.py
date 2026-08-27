"""
OBS Studio WebSocket服务
用于与OBS Studio进行通信，控制推流和录制
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any
from websockets.client import connect
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)


class OBSService:
    """OBS WebSocket服务类"""
    
    def __init__(self, host: str = "localhost", port: int = 4444, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.password = password
        self.websocket = None
        self.message_id = 0
        self.connected = False
        
    async def connect(self):
        """连接到OBS WebSocket服务器"""
        try:
            self.websocket = await connect(f"ws://{self.host}:{self.port}")
            
            # 发送认证请求（如果需要密码）
            if self.password:
                auth_response = await self._send_request("Authenticate", {
                    "auth": self.password
                })
                
                if not auth_response.get("status"):
                    raise Exception("OBS认证失败")
            
            # 获取OBS版本信息
            version_info = await self._send_request("GetVersion")
            logger.info(f"已连接到OBS Studio v{version_info.get('obsVersion', '未知')}")
            
            self.connected = True
            return True
            
        except Exception as e:
            logger.error(f"连接OBS失败: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """断开与OBS的连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        self.connected = False
    
    async def _send_request(self, request_type: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送WebSocket请求"""
        if not self.websocket:
            raise Exception("WebSocket未连接")
        
        self.message_id += 1
        request = {
            "request-type": request_type,
            "message-id": str(self.message_id)
        }
        
        if data:
            request.update(data)
        
        await self.websocket.send(json.dumps(request))
        response = await self.websocket.recv()
        
        return json.loads(response)
    
    async def start_streaming(self, stream_key: str, server_url: str = "rtmp://localhost:1935/live"):
        """开始推流"""
        try:
            # 设置推流参数
            await self._send_request("SetStreamSettings", {
                "type": "rtmp_common",
                "settings": {
                    "server": server_url,
                    "key": stream_key
                }
            })
            
            # 开始推流
            response = await self._send_request("StartStreaming")
            
            if response.get("status") == "ok":
                logger.info("OBS推流已开始")
                return True
            else:
                logger.error(f"开始推流失败: {response}")
                return False
                
        except Exception as e:
            logger.error(f"开始推流时出错: {e}")
            return False
    
    async def stop_streaming(self):
        """停止推流"""
        try:
            response = await self._send_request("StopStreaming")
            
            if response.get("status") == "ok":
                logger.info("OBS推流已停止")
                return True
            else:
                logger.error(f"停止推流失败: {response}")
                return False
                
        except Exception as e:
            logger.error(f"停止推流时出错: {e}")
            return False
    
    async def start_recording(self):
        """开始录制"""
        try:
            response = await self._send_request("StartRecording")
            
            if response.get("status") == "ok":
                logger.info("OBS录制已开始")
                return True
            else:
                logger.error(f"开始录制失败: {response}")
                return False
                
        except Exception as e:
            logger.error(f"开始录制时出错: {e}")
            return False
    
    async def stop_recording(self):
        """停止录制"""
        try:
            response = await self._send_request("StopRecording")
            
            if response.get("status") == "ok":
                logger.info("OBS录制已停止")
                return True
            else:
                logger.error(f"停止录制失败: {response}")
                return False
                
        except Exception as e:
            logger.error(f"停止录制时出错: {e}")
            return False
    
    async def get_stream_status(self):
        """获取推流状态"""
        try:
            response = await self._send_request("GetStreamingStatus")
            
            return {
                "streaming": response.get("streaming", False),
                "recording": response.get("recording", False),
                "stream_timecode": response.get("stream-timecode", ""),
                "rec_timecode": response.get("rec-timecode", "")
            }
            
        except Exception as e:
            logger.error(f"获取推流状态失败: {e}")
            return {"streaming": False, "recording": False}
    
    async def set_scene(self, scene_name: str):
        """切换场景"""
        try:
            response = await self._send_request("SetCurrentScene", {
                "scene-name": scene_name
            })
            
            if response.get("status") == "ok":
                logger.info(f"已切换到场景: {scene_name}")
                return True
            else:
                logger.error(f"切换场景失败: {response}")
                return False
                
        except Exception as e:
            logger.error(f"切换场景时出错: {e}")
            return False
    
    async def get_scenes(self):
        """获取场景列表"""
        try:
            response = await self._send_request("GetSceneList")
            
            scenes = []
            for scene in response.get("scenes", []):
                scenes.append({
                    "name": scene.get("name"),
                    "sources": scene.get("sources", [])
                })
            
            return scenes
            
        except Exception as e:
            logger.error(f"获取场景列表失败: {e}")
            return []
    
    async def set_stream_title(self, title: str):
        """设置流媒体标题"""
        try:
            # 设置流媒体服务设置中的流密钥（用于包含标题信息）
            response = await self._send_request("SetStreamSettings", {
                "type": "rtmp_common",
                "settings": {
                    "server": "rtmp://localhost:1935/live",
                    "key": f"{title}"
                }
            })
            
            return response.get("status") == "ok"
            
        except Exception as e:
            logger.error(f"设置流标题失败: {e}")
            return False


# 全局OBS服务实例
obs_service = OBSService()


async def get_obs_service() -> OBSService:
    """获取OBS服务实例"""
    return obs_service