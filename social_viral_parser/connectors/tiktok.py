from __future__ import annotations
from typing import Iterable, List, Optional
from datetime import datetime
from ..models import ContentItem, Author

try:
	from TikTokApi import TikTokApi
except Exception:  # pragma: no cover - optional
	TikTokApi = None  # type: ignore


class TikTokConnector:
	def __init__(self, ms_token: Optional[str] = None):
		if TikTokApi is None:
			raise RuntimeError("TikTokApi is not installed or failed to import.")
		self.ms_token = ms_token

	def search_hashtags(self, hashtags: Iterable[str], max_results: int = 50) -> List[ContentItem]:
		items: List[ContentItem] = []
		with TikTokApi() as api:
			if self.ms_token:
				api._get_ms_token = lambda: self.ms_token  # noqa: E731
			for tag in hashtags:
				hs = api.hashtag(name=tag)
				for v in hs.videos(count=min(max_results, 100)):
					stats = v.stats
					aweme = v.as_dict
					items.append(ContentItem(
						platform="tiktok",
						id=str(aweme.get("id")),
						url=f"https://www.tiktok.com/@{aweme.get('author', {}).get('uniqueId')}/video/{aweme.get('id')}",
						title=aweme.get("desc"),
						description=aweme.get("desc"),
						published_at=datetime.fromtimestamp(int(aweme.get("createTime", 0))) if aweme.get("createTime") else None,
						author=Author(platform="tiktok", id=str(aweme.get('author', {}).get('id', '')), username=aweme.get('author', {}).get('uniqueId')),
						views=stats.get("playCount"),
						likes=stats.get("diggCount"),
						comments=stats.get("commentCount"),
						shares=stats.get("shareCount"),
						hashtags=[t.get('name') for t in aweme.get('challenges', []) if t.get('name')],
					))
		return items