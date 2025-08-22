from __future__ import annotations
from typing import Iterable, List, Dict
import pandas as pd
from ..models import ContentItem


def to_rows(items: Iterable[ContentItem]) -> list[dict]:
	rows: list[dict] = []
	for it in items:
		rows.append({
			"platform": it.platform,
			"id": it.id,
			"url": it.url,
			"title": it.title,
			"description": it.description,
			"published_at": it.published_at.isoformat() if it.published_at else None,
			"author_id": it.author.id if it.author else None,
			"author_name": it.author.name if it.author else None,
			"author_followers": it.author.followers if it.author else None,
			"views": it.views,
			"likes": it.likes,
			"comments": it.comments,
			"shares": it.shares,
			"duration_seconds": it.duration_seconds,
			"hashtags": ",".join(it.hashtags) if it.hashtags else None,
			"tags": ",".join(it.tags) if it.tags else None,
			"niche": it.niche,
		})
	return rows


def export_csv(items: Iterable[ContentItem], csv_path: str) -> None:
	rows = to_rows(items)
	df = pd.DataFrame(rows)
	df.to_csv(csv_path, index=False)


def export_rows_to_csv(rows: List[Dict], csv_path: str) -> None:
	df = pd.DataFrame(rows)
	df.to_csv(csv_path, index=False)