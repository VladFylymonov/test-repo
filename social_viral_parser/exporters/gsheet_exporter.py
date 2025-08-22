from __future__ import annotations
from typing import Iterable, List, Dict
import gspread
from ..models import ContentItem
from .csv_exporter import to_rows


def export_gsheet(items: Iterable[ContentItem], service_account_json: str, spreadsheet_key: str, worksheet: str = "Results", share_with: list[str] | None = None) -> None:
	gc = gspread.service_account(filename=service_account_json)
	sh = gc.open_by_key(spreadsheet_key)
	try:
		ws = sh.worksheet(worksheet)
	except gspread.WorksheetNotFound:
		ws = sh.add_worksheet(title=worksheet, rows=1000, cols=30)
	rows = to_rows(items)
	# Prepare header + rows
	if not rows:
		ws.clear()
		ws.update("A1", [["platform","id","url","title","description","published_at","author_id","author_name","author_followers","views","likes","comments","shares","duration_seconds","hashtags","tags","niche"]])
		return
	header = list(rows[0].keys())
	values = [header] + [[r.get(k) for k in header] for r in rows]
	ws.clear()
	ws.update("A1", values)
	if share_with:
		for email in share_with:
			try:
				sh.share(email, perm_type='user', role='reader', notify=False)
			except Exception:
				continue


def export_rows_to_gsheet(rows: List[Dict], service_account_json: str, spreadsheet_key: str, worksheet: str, share_with: list[str] | None = None) -> None:
	gc = gspread.service_account(filename=service_account_json)
	sh = gc.open_by_key(spreadsheet_key)
	try:
		ws = sh.worksheet(worksheet)
	except gspread.WorksheetNotFound:
		ws = sh.add_worksheet(title=worksheet, rows=200, cols=20)
	if not rows:
		ws.clear()
		return
	header = list(rows[0].keys())
	values = [header] + [[r.get(k) for k in header] for r in rows]
	ws.clear()
	ws.update("A1", values)
	if share_with:
		for email in share_with:
			try:
				sh.share(email, perm_type='user', role='reader', notify=False)
			except Exception:
				continue