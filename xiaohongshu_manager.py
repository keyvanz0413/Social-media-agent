"""Backward-compatible xiaohongshu manager wrapper."""
from social_media_agent.xiaohongshu_manager import *  # noqa: F401,F403

if __name__ == "__main__":
    from social_media_agent.xiaohongshu_manager import main
    main()
