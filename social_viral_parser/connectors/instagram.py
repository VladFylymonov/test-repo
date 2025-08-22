from __future__ import annotations
from typing import Iterable, List, Optional
import requests
from datetime import datetime
from dateutil import parser as date_parser
from ..models import ContentItem, Author


GRAPH_BASE = "https://graph.facebook.com/v19.0"


class InstagramConnector:
	def __init__(self, access_token: str, business_account_id: str):
		self.access_token = access_token
		self.business_account_id = business_account_id

	def _get(self, path: str, params: dict | None = None) -> dict:
		params = params or {}
		params["access_token"] = self.access_token
		r = requests.get(f"{GRAPH_BASE}/{path}", params=params, timeout=30)
		r.raise_for_status()
		return r.json()

	def search_hashtag(self, hashtag_name: str) -> Optional[str]:
		data = self._get(f"ig_hashtag_search", {"user_id": self.business_account_id, "q": hashtag_name})
		ids = data.get("data", [])
		return ids[0]["id"] if ids else None

	def fetch_hashtag_media(self, hashtag_id: str, limit: int = 50) -> List[ContentItem]:
		params = {
			"user_id": self.business_account_id,
			"fields": "id,caption,comments_count,like_count,media_type,media_url,permalink,timestamp,username",
			"limit": min(limit, 50),
		}
		data = self._get(f"{hashtag_id}/recent_media", params)
		items: List[ContentItem] = []
		for m in data.get("data", []):
			published_at = date_parser.parse(m.get("timestamp")) if m.get("timestamp") else None
			caption = m.get("caption") or ""
			url = m.get("permalink")
			author_username = m.get("username")
			likes = m.get("like_count")
			comments = m.get("comments_count")
			hashtags = _extract_hashtags(caption)
			items.append(ContentItem(
				platform="instagram",
				id=m.get("id"),
				url=url,
				title=caption[:120] if caption else None,
				description=caption,
				published_at=published_at,
				author=Author(platform="instagram", id=author_username or "", username=author_username),
				likes=int(likes) if likes is not None else None,
				comments=int(comments) if comments is not None else None,
				hashtags=hashtags,
			))
		return items

	def get_user_followers(self, user_id: str) -> Optional[int]:
		# Only works for business accounts you manage
		try:
			data = self._get(f"{user_id}", {"fields": "followers_count"})
			return int(data.get("followers_count")) if data.get("followers_count") is not None else None
		except requests.HTTPError:
			return None

	def get_user_profile(self, user_id: str) -> Optional[dict]:
		try:
			data = self._get(f"{user_id}", {"fields": "username,followers_count,media_count"})
			return data
		except requests.HTTPError:
			return None


def _extract_hashtags(text: str) -> List[str]:
	if not text:
		return []
	result: List[str] = []
	for token in text.split():
		if token.startswith('#') and len(token) > 1:
			result.append(token[1:].strip('.,!?:;'))
	return result