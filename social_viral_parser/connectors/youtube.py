from __future__ import annotations
from typing import Iterable, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from dateutil import parser as date_parser
from ..models import ContentItem, Author


class YouTubeConnector:
	def __init__(self, api_key: str):
		self.api_key = api_key
		self.service = build("youtube", "v3", developerKey=api_key, cache_discovery=False)

	def search(self, queries: Iterable[str], max_results: int = 50) -> List[ContentItem]:
		items: List[ContentItem] = []
		for query in queries:
			try:
				resp = self.service.search().list(
					part="id,snippet",
					q=query,
					type="video",
					maxResults=min(max_results, 50),
					order="viewCount",
				).execute()
				video_ids = [it["id"]["videoId"] for it in resp.get("items", []) if it.get("id", {}).get("videoId")]
				if not video_ids:
					continue
				items.extend(self._videos_to_items(video_ids))
			except HttpError:
				continue
		return items

	def _videos_to_items(self, video_ids: List[str]) -> List[ContentItem]:
		videos_resp = self.service.videos().list(
			part="snippet,contentDetails,statistics",
			id=",".join(video_ids),
		).execute()
		items: List[ContentItem] = []
		for v in videos_resp.get("items", []):
			vid = v["id"]
			snippet = v.get("snippet", {})
			stats = v.get("statistics", {})
			content_details = v.get("contentDetails", {})
			channel_id = snippet.get("channelId")
			channel_title = snippet.get("channelTitle")
			published_at_str = snippet.get("publishedAt")
			published_at = date_parser.parse(published_at_str) if published_at_str else None
			url = f"https://www.youtube.com/watch?v={vid}"
			likes = int(stats.get("likeCount", 0)) if stats.get("likeCount") is not None else None
			views = int(stats.get("viewCount", 0)) if stats.get("viewCount") is not None else None
			comments = int(stats.get("commentCount", 0)) if stats.get("commentCount") is not None else None
			tags = snippet.get("tags", []) or []
			# duration in PT#M#S
			duration_seconds = _parse_iso8601_duration_to_seconds(content_details.get("duration")) if content_details.get("duration") else None
			items.append(ContentItem(
				platform="youtube",
				id=vid,
				url=url,
				title=snippet.get("title"),
				description=snippet.get("description"),
				published_at=published_at,
				author=Author(platform="youtube", id=channel_id or "", name=channel_title),
				views=views,
				likes=likes,
				comments=comments,
				duration_seconds=duration_seconds,
				tags=tags,
			))
		return items

	def get_channel_subscribers(self, channel_id: str) -> Optional[int]:
		resp = self.service.channels().list(part="statistics", id=channel_id).execute()
		items = resp.get("items", [])
		if not items:
			return None
		stats = items[0].get("statistics", {})
		return int(stats.get("subscriberCount")) if stats.get("subscriberCount") is not None else None

	def get_channel_statistics(self, channel_id: str) -> Optional[dict]:
		try:
			resp = self.service.channels().list(part="statistics,snippet", id=channel_id).execute()
			items = resp.get("items", [])
			if not items:
				return None
			ch = items[0]
			stats = ch.get("statistics", {})
			snippet = ch.get("snippet", {})
			return {
				"title": snippet.get("title"),
				"viewCount": int(stats.get("viewCount", 0)) if stats.get("viewCount") is not None else None,
				"subscriberCount": int(stats.get("subscriberCount", 0)) if stats.get("subscriberCount") is not None else None,
				"videoCount": int(stats.get("videoCount", 0)) if stats.get("videoCount") is not None else None,
			}
		except HttpError:
			return None

_DEF_UNITS = {
	"H": 3600,
	"M": 60,
	"S": 1,
}


def _parse_iso8601_duration_to_seconds(duration: str) -> int:
	# Example: PT1H2M3S
	if not duration.startswith("PT"):
		return 0
	seconds = 0
	current = ""
	for ch in duration[2:]:
		if ch.isdigit():
			current += ch
		else:
			seconds += int(current or 0) * _DEF_UNITS.get(ch, 0)
			current = ""
	return seconds