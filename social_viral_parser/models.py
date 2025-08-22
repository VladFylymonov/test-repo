from __future__ import annotations
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field
from datetime import datetime


Platform = Literal["youtube", "instagram", "tiktok"]


class Author(BaseModel):
	platform: Platform
	id: str
	username: Optional[str] = None
	name: Optional[str] = None
	followers: Optional[int] = None


class ContentItem(BaseModel):
	platform: Platform
	id: str
	url: str
	title: Optional[str] = None
	description: Optional[str] = None
	published_at: Optional[datetime] = None
	author: Optional[Author] = None
	views: Optional[int] = None
	likes: Optional[int] = None
	comments: Optional[int] = None
	shares: Optional[int] = None
	duration_seconds: Optional[int] = None
	hashtags: List[str] = Field(default_factory=list)
	tags: List[str] = Field(default_factory=list)
	niche: Optional[str] = None
	extra: Dict[str, str] = Field(default_factory=dict)


class Criteria(BaseModel):
	niches: List[str] = Field(default_factory=list, description="List of niche keywords to search for")
	hashtags: List[str] = Field(default_factory=list, description="Hashtags without #, e.g., ['marketing', 'fitness']")
	min_views: Optional[int] = None
	min_likes: Optional[int] = None
	min_comments: Optional[int] = None
	min_shares: Optional[int] = None
	min_like_view_ratio: Optional[float] = Field(default=None, description="likes/views >= ratio")
	published_after: Optional[datetime] = None
	published_before: Optional[datetime] = None
	max_results_per_source: int = 100


class OwnAccountsConfig(BaseModel):
	youtube_channel_ids: List[str] = Field(default_factory=list)
	instagram_user_ids: List[str] = Field(default_factory=list, description="Business account IDs you manage")


class OwnMetric(BaseModel):
	platform: Platform
	id: str
	username: Optional[str] = None
	name: Optional[str] = None
	followers: Optional[int] = None
	subscribers: Optional[int] = None
	view_count: Optional[int] = None
	video_count: Optional[int] = None
	media_count: Optional[int] = None
	timestamp: datetime = Field(default_factory=datetime.utcnow)


class RunConfig(BaseModel):
	platforms: List[Platform] = Field(default_factory=lambda: ["youtube", "instagram", "tiktok"])
	criteria: Criteria
	export: "ExportConfig"
	credentials: "CredentialsConfig"
	own_accounts: Optional[OwnAccountsConfig] = None
	schedule: Optional["ScheduleConfig"] = None


class ExportConfig(BaseModel):
	csv_path: Optional[str] = None
	own_metrics_csv_path: Optional[str] = None
	google_sheets: Optional["GoogleSheetsConfig"] = None


class GoogleSheetsConfig(BaseModel):
	service_account_json: str
	spreadsheet_key: str
	worksheet: str = "Results"
	own_metrics_worksheet: str = "OwnMetrics"
	share_with: List[str] = Field(default_factory=list)


class CredentialsConfig(BaseModel):
	youtube_api_key: Optional[str] = None
	instagram_access_token: Optional[str] = None
	instagram_business_account_id: Optional[str] = None
	tiktok_ms_token: Optional[str] = None


class ScheduleConfig(BaseModel):
	cron: Optional[str] = None
	interval_minutes: Optional[int] = None


__all__ = [
	"Platform",
	"Author",
	"ContentItem",
	"Criteria",
	"OwnAccountsConfig",
	"OwnMetric",
	"RunConfig",
	"ExportConfig",
	"GoogleSheetsConfig",
	"CredentialsConfig",
	"ScheduleConfig",
]