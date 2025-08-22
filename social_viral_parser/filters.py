from __future__ import annotations
from typing import Iterable, List
from .models import ContentItem, Criteria


def filter_items(items: Iterable[ContentItem], criteria: Criteria) -> List[ContentItem]:
	result: List[ContentItem] = []
	for item in items:
		if criteria.published_after and item.published_at and item.published_at < criteria.published_after:
			continue
		if criteria.published_before and item.published_at and item.published_at > criteria.published_before:
			continue
		if criteria.min_views is not None and (item.views or 0) < criteria.min_views:
			continue
		if criteria.min_likes is not None and (item.likes or 0) < criteria.min_likes:
			continue
		if criteria.min_comments is not None and (item.comments or 0) < criteria.min_comments:
			continue
		if criteria.min_shares is not None and (item.shares or 0) < criteria.min_shares:
			continue
		if criteria.min_like_view_ratio is not None and item.views and item.likes is not None:
			if item.views > 0 and (item.likes / item.views) < criteria.min_like_view_ratio:
				continue
		result.append(item)
	return result