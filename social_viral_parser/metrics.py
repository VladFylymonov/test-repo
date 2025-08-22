from __future__ import annotations
from typing import List
from datetime import datetime
from .models import OwnMetric, RunConfig
from .connectors.youtube import YouTubeConnector
from .connectors.instagram import InstagramConnector


def collect_own_metrics(cfg: RunConfig) -> List[OwnMetric]:
	metrics: List[OwnMetric] = []
	if not cfg.own_accounts:
		return metrics

	# YouTube channels by ID via API key
	if cfg.credentials.youtube_api_key and cfg.own_accounts.youtube_channel_ids:
		yt = YouTubeConnector(cfg.credentials.youtube_api_key)
		for cid in cfg.own_accounts.youtube_channel_ids:
			stats = yt.get_channel_statistics(cid)
			if not stats:
				continue
			m = OwnMetric(
				platform="youtube",
				id=cid,
				name=stats.get("title"),
				subscribers=stats.get("subscriberCount"),
				view_count=stats.get("viewCount"),
				video_count=stats.get("videoCount"),
			)
			metrics.append(m)

	# Instagram business accounts by ID
	if cfg.credentials.instagram_access_token and cfg.own_accounts.instagram_user_ids:
		ig = InstagramConnector(cfg.credentials.instagram_access_token, cfg.credentials.instagram_business_account_id or "")
		for uid in cfg.own_accounts.instagram_user_ids:
			data = ig.get_user_profile(uid)
			if not data:
				continue
			m = OwnMetric(
				platform="instagram",
				id=uid,
				username=data.get("username"),
				followers=data.get("followers_count"),
				media_count=data.get("media_count"),
			)
			metrics.append(m)

	return metrics