"""
MCP Client Wrapper
封装小红书 MCP 的调用逻辑
"""

from typing import Dict, Any, List, Optional
import requests
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logger = logging.getLogger(__name__)


class XiaohongshuMCPError(Exception):
    """小红书MCP客户端异常"""
    pass


class XiaohongshuMCPClient:
    """小红书 MCP 客户端封装"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:18060",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        初始化 MCP 客户端
        
        Args:
            base_url: MCP 服务器地址（默认：http://localhost:18060）
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.base_url = base_url.rstrip('/')
        self.api_base_url = f"{self.base_url}/api/v1"
        self.timeout = timeout
        
        # 配置带重试机制的session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"初始化小红书MCP客户端: {self.base_url}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        发起HTTP请求的通用方法
        
        Args:
            method: HTTP方法（GET/POST）
            endpoint: API端点
            data: 请求数据
            timeout: 请求超时（如果不指定则使用默认值）
            
        Returns:
            响应数据
            
        Raises:
            XiaohongshuMCPError: 请求失败时抛出
        """
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        timeout = timeout or self.timeout
        
        try:
            logger.debug(f"发起{method}请求: {url}")
            if data:
                logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
            
            if method.upper() == "GET":
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=timeout)
            else:
                raise XiaohongshuMCPError(f"不支持的HTTP方法: {method}")
            
            # 检查HTTP状态码
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise XiaohongshuMCPError(error_msg)
            
            # 解析响应
            result = response.json()
            logger.debug(f"响应数据: {json.dumps(result, ensure_ascii=False)}")
            
            # 检查业务状态
            if not result.get('success', False):
                error_msg = result.get('message', '未知错误')
                logger.error(f"API返回失败: {error_msg}")
                raise XiaohongshuMCPError(error_msg)
            
            return result.get('data', {})
            
        except requests.exceptions.Timeout:
            error_msg = f"请求超时（{timeout}秒）: {url}"
            logger.error(error_msg)
            raise XiaohongshuMCPError(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"连接失败: {str(e)}"
            logger.error(error_msg)
            raise XiaohongshuMCPError(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析失败: {str(e)}"
            logger.error(error_msg)
            raise XiaohongshuMCPError(error_msg)
        except Exception as e:
            if isinstance(e, XiaohongshuMCPError):
                raise
            error_msg = f"请求失败: {str(e)}"
            logger.error(error_msg)
            raise XiaohongshuMCPError(error_msg)
    
    def check_health(self) -> bool:
        """
        检查 MCP 服务健康状态
        
        Returns:
            True 如果服务正常，False 如果服务不可用
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> if client.check_health():
            ...     print("服务正常")
        """
        # Mock 模式检查
        from config import DevConfig
        if DevConfig.MOCK_MODE:
            logger.info("🎭 Mock 模式：模拟 MCP 健康检查")
            return True
        
        try:
            # 尝试检查登录状态，如果能成功请求则说明服务正常
            self.check_login_status()
            return True
        except Exception as e:
            logger.warning(f"健康检查失败: {str(e)}")
            return False
    
    def check_login_status(self) -> Dict[str, Any]:
        """
        检查小红书登录状态
        
        Returns:
            登录状态信息，包含：
            - is_logged_in: 是否已登录
            - username: 用户名（如果已登录）
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> status = client.check_login_status()
            >>> print(status['is_logged_in'])
        """
        # Mock 模式检查
        from config import DevConfig
        if DevConfig.MOCK_MODE:
            logger.info("🎭 Mock 模式：模拟登录状态检查")
            from utils.mock_data import MockDataGenerator
            return MockDataGenerator.mock_login_status(logged_in=True)
        
        logger.info("检查登录状态")
        return self._make_request("GET", "/login/status")
    
    def search_notes(
        self,
        keyword: str,
        limit: int = 10,
        sort_by: str = "general",
        note_type: str = "",
        publish_time: str = ""
    ) -> Dict[str, Any]:
        """
        搜索小红书笔记
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量（默认10）
            sort_by: 排序方式（general=综合, popularity_descending=最热, time_descending=最新）
            note_type: 笔记类型（空=全部, video=视频, normal=图文）
            publish_time: 发布时间（空=全部, 1day=一天内, 1week=一周内, 1month=一月内）
            
        Returns:
            包含笔记列表的字典：
            - feeds: 笔记列表
            - total: 总数
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> result = client.search_notes("澳洲旅游", limit=5)
            >>> for feed in result['feeds']:
            >>>     print(feed['title'])
        """
        # Mock 模式检查
        from config import DevConfig
        if DevConfig.MOCK_MODE:
            logger.info(f"🎭 Mock 模式：模拟搜索笔记 ({keyword})")
            from utils.mock_data import MockDataGenerator
            return MockDataGenerator.mock_xiaohongshu_search(keyword, limit)
        
        logger.info(f"搜索笔记: {keyword}, 数量: {limit}")
        
        data = {
            "keyword": keyword,
            "limit": limit,
            "filters": {
                "sort_by": sort_by,
                "note_type": note_type,
                "publish_time": publish_time
            }
        }
        
        return self._make_request("POST", "/feeds/search", data=data, timeout=15)
    
    def get_note_detail(self, note_id: str, xsec_token: str) -> Dict[str, Any]:
        """
        获取笔记详情
        
        Args:
            note_id: 笔记ID
            xsec_token: 安全令牌（从搜索结果或列表中获取）
            
        Returns:
            笔记详细信息，包含：
            - title: 标题
            - content: 内容
            - images: 图片列表
            - user: 用户信息
            - stats: 互动数据（点赞、收藏、评论数）
            - comments: 评论列表
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> detail = client.get_note_detail("note_id_123", "xsec_token_abc")
            >>> print(detail['title'])
        """
        logger.info(f"获取笔记详情: {note_id}")
        
        data = {
            "feed_id": note_id,
            "xsec_token": xsec_token
        }
        
        return self._make_request("POST", "/feeds/detail", data=data, timeout=15)
    
    def list_feeds(self, limit: int = 20) -> Dict[str, Any]:
        """
        获取小红书首页推荐列表
        
        Args:
            limit: 返回数量（默认20）
            
        Returns:
            包含推荐笔记列表的字典：
            - feeds: 笔记列表
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> result = client.list_feeds(limit=10)
            >>> for feed in result['feeds']:
            >>>     print(feed['title'])
        """
        logger.info(f"获取推荐列表, 数量: {limit}")
        return self._make_request("GET", f"/feeds/list?limit={limit}", timeout=15)
    
    def publish_note(
        self,
        title: str,
        content: str,
        images: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        发布图文笔记到小红书
        
        Args:
            title: 标题（不超过20个字）
            content: 正文（不超过1000个字）
            images: 图片路径列表（支持本地路径或HTTP链接，推荐本地路径）
            tags: 标签列表
            
        Returns:
            发布结果，包含：
            - success: 是否成功
            - note_id: 笔记ID（如果成功）
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> result = client.publish_note(
            >>>     title="美丽的春天",
            >>>     content="春天来了，花儿都开了",
            >>>     images=["/path/to/image1.jpg", "/path/to/image2.jpg"],
            >>>     tags=["春天", "旅游"]
            >>> )
        """
        # Mock 模式检查
        from config import DevConfig
        if DevConfig.MOCK_MODE:
            logger.info(f"🎭 Mock 模式：模拟发布笔记 ({title})")
            from utils.mock_data import MockDataGenerator
            return MockDataGenerator.mock_publish_result(success=True)
        
        logger.info(f"发布图文笔记: {title}")
        
        if not title or len(title) > 20:
            raise XiaohongshuMCPError("标题不能为空且不能超过20个字")
        
        if not content or len(content) > 1000:
            raise XiaohongshuMCPError("正文不能为空且不能超过1000个字")
        
        data = {
            "title": title,
            "content": content,
            "images": images or [],
            "tags": tags or []
        }
        
        return self._make_request("POST", "/publish", data=data, timeout=60)
    
    def publish_video(
        self,
        title: str,
        content: str,
        video_path: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        发布视频笔记到小红书
        
        Args:
            title: 标题（不超过20个字）
            content: 正文（不超过1000个字）
            video_path: 本地视频文件路径（仅支持本地路径）
            tags: 标签列表
            
        Returns:
            发布结果
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> result = client.publish_video(
            >>>     title="美食教程",
            >>>     content="教你做美味佳肴",
            >>>     video_path="/path/to/video.mp4",
            >>>     tags=["美食", "教程"]
            >>> )
        """
        logger.info(f"发布视频笔记: {title}")
        
        if not title or len(title) > 20:
            raise XiaohongshuMCPError("标题不能为空且不能超过20个字")
        
        if not content or len(content) > 1000:
            raise XiaohongshuMCPError("正文不能为空且不能超过1000个字")
        
        if not video_path:
            raise XiaohongshuMCPError("视频路径不能为空")
        
        data = {
            "title": title,
            "content": content,
            "video": video_path,
            "tags": tags or []
        }
        
        return self._make_request("POST", "/publish/video", data=data, timeout=120)
    
    def post_comment(
        self,
        note_id: str,
        xsec_token: str,
        content: str
    ) -> Dict[str, Any]:
        """
        发表评论到笔记
        
        Args:
            note_id: 笔记ID
            xsec_token: 安全令牌
            content: 评论内容
            
        Returns:
            评论结果
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> result = client.post_comment("note_id_123", "token_abc", "很棒的分享！")
        """
        logger.info(f"发表评论到笔记: {note_id}")
        
        data = {
            "feed_id": note_id,
            "xsec_token": xsec_token,
            "content": content
        }
        
        return self._make_request("POST", "/feeds/comment", data=data, timeout=15)
    
    def get_user_profile(self, user_id: str, xsec_token: str) -> Dict[str, Any]:
        """
        获取用户个人主页信息
        
        Args:
            user_id: 用户ID
            xsec_token: 安全令牌
            
        Returns:
            用户信息，包含：
            - user: 用户基本信息
            - stats: 统计数据（关注数、粉丝数等）
            - notes: 用户发布的笔记列表
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> profile = client.get_user_profile("user_id_123", "token_abc")
            >>> print(profile['user']['nickname'])
        """
        logger.info(f"获取用户主页: {user_id}")
        
        data = {
            "user_id": user_id,
            "xsec_token": xsec_token
        }
        
        return self._make_request("POST", "/user/profile", data=data, timeout=15)
    
    def like_note(self, note_id: str, xsec_token: str, unlike: bool = False) -> Dict[str, Any]:
        """
        点赞或取消点赞笔记
        
        Args:
            note_id: 笔记ID
            xsec_token: 安全令牌
            unlike: True表示取消点赞，False表示点赞
            
        Returns:
            操作结果
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> # 点赞
            >>> result = client.like_note("note_id_123", "token_abc")
            >>> # 取消点赞
            >>> result = client.like_note("note_id_123", "token_abc", unlike=True)
        """
        action = "取消点赞" if unlike else "点赞"
        logger.info(f"{action}笔记: {note_id}")
        
        data = {
            "feed_id": note_id,
            "xsec_token": xsec_token,
            "unlike": unlike
        }
        
        return self._make_request("POST", "/feeds/like", data=data, timeout=15)
    
    def favorite_note(self, note_id: str, xsec_token: str, unfavorite: bool = False) -> Dict[str, Any]:
        """
        收藏或取消收藏笔记
        
        Args:
            note_id: 笔记ID
            xsec_token: 安全令牌
            unfavorite: True表示取消收藏，False表示收藏
            
        Returns:
            操作结果
            
        Example:
            >>> client = XiaohongshuMCPClient()
            >>> # 收藏
            >>> result = client.favorite_note("note_id_123", "token_abc")
            >>> # 取消收藏
            >>> result = client.favorite_note("note_id_123", "token_abc", unfavorite=True)
        """
        action = "取消收藏" if unfavorite else "收藏"
        logger.info(f"{action}笔记: {note_id}")
        
        data = {
            "feed_id": note_id,
            "xsec_token": xsec_token,
            "unfavorite": unfavorite
        }
        
        return self._make_request("POST", "/feeds/favorite", data=data, timeout=15)
    
    def close(self):
        """关闭HTTP会话"""
        self.session.close()
        logger.info("MCP客户端已关闭")
    
    def __enter__(self):
        """支持上下文管理器"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        self.close()

