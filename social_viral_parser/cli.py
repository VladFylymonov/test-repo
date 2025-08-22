from __future__ import annotations
import argparse
import time
from typing import List, Optional
from .config import load_config
from .models import ContentItem
from .filters import filter_items
from .utils.logging import setup_logging
from .connectors.youtube import YouTubeConnector
from .connectors.instagram import InstagramConnector
from .connectors.tiktok import TikTokConnector
from .exporters.csv_exporter import export_csv, export_rows_to_csv
from .exporters.gsheet_exporter import export_gsheet, export_rows_to_gsheet
from .metrics import collect_own_metrics


def _is_placeholder(value: Optional[str]) -> bool:
	return bool(value) and value.startswith("YOUR_")


def run_once(config_path: str) -> List[ContentItem]:
	cfg = load_config(config_path)
	setup_logging()
	all_items: List[ContentItem] = []

	criteria = cfg.criteria
	max_results = criteria.max_results_per_source

	if (
		"youtube" in cfg.platforms
		and cfg.credentials.youtube_api_key
		and not _is_placeholder(cfg.credentials.youtube_api_key)
	):
		yt = YouTubeConnector(cfg.credentials.youtube_api_key)
		queries = list(criteria.niches) + [f"#{h}" for h in criteria.hashtags]
		all_items.extend(yt.search(queries, max_results=max_results))

	if (
		"instagram" in cfg.platforms
		and cfg.credentials.instagram_access_token
		and cfg.credentials.instagram_business_account_id
		and not _is_placeholder(cfg.credentials.instagram_access_token)
		and not _is_placeholder(cfg.credentials.instagram_business_account_id)
	):
		ig = InstagramConnector(cfg.credentials.instagram_access_token, cfg.credentials.instagram_business_account_id)
		for h in criteria.hashtags:
			try:
				hid = ig.search_hashtag(h)
				if not hid:
					continue
				all_items.extend(ig.fetch_hashtag_media(hid, limit=max_results))
			except Exception:
				continue

	if (
		"tiktok" in cfg.platforms
		and cfg.credentials.tiktok_ms_token
		and not _is_placeholder(cfg.credentials.tiktok_ms_token)
	):
		try:
			tt = TikTokConnector(cfg.credentials.tiktok_ms_token)
			all_items.extend(tt.search_hashtags(criteria.hashtags, max_results=max_results))
		except Exception:
			pass

	filtered = filter_items(all_items, criteria)

	# Export content items
	if cfg.export.csv_path:
		export_csv(filtered, cfg.export.csv_path)
	if cfg.export.google_sheets:
		export_gsheet(
			filtered,
			cfg.export.google_sheets.service_account_json,
			cfg.export.google_sheets.spreadsheet_key,
			cfg.export.google_sheets.worksheet,
			cfg.export.google_sheets.share_with,
		)

	# Collect and export own account metrics if configured
	own_metrics = collect_own_metrics(cfg)
	if own_metrics:
		rows = []
		for m in own_metrics:
			rows.append({
				"platform": m.platform,
				"id": m.id,
				"username": m.username,
				"name": m.name,
				"followers": m.followers,
				"subscribers": m.subscribers,
				"view_count": m.view_count,
				"video_count": m.video_count,
				"media_count": m.media_count,
				"timestamp": m.timestamp.isoformat(),
			})
		if cfg.export.own_metrics_csv_path:
			export_rows_to_csv(rows, cfg.export.own_metrics_csv_path)
		if cfg.export.google_sheets:
			export_rows_to_gsheet(
				rows,
				cfg.export.google_sheets.service_account_json,
				cfg.export.google_sheets.spreadsheet_key,
				cfg.export.google_sheets.own_metrics_worksheet,
				cfg.export.google_sheets.share_with,
			)

	return filtered


def main() -> None:
	parser = argparse.ArgumentParser(description="Social viral content parser")
	parser.add_argument("config", help="Path to YAML config")
	parser.add_argument("--schedule", action="store_true", help="Start scheduler defined in config")
	args = parser.parse_args()

	if args.schedule:
		from .scheduler import RunnerScheduler
		cfg = load_config(args.config)
		def job():
			run_once(args.config)
		s = RunnerScheduler()
		s.start()
		s.schedule(cfg.schedule, job)
		try:
			while True:
				time.sleep(5)
		except KeyboardInterrupt:
			pass
		finally:
			s.shutdown()
	else:
		run_once(args.config)


if __name__ == "__main__":
	main()