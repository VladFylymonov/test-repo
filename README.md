# Social Viral Parser

Collect viral videos from Instagram, YouTube, and TikTok by niches/hashtags, filter by metrics, and export to CSV or Google Sheets. Supports scheduled runs.

## Setup

1. Create virtualenv and install deps:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

See `config.example.yaml` and copy to `config.yaml`.
- Fill API credentials:
  - YouTube Data API v3 key
  - Instagram Graph API: `access_token`, `business_account_id`
  - TikTok (optional): `ms_token`
- Choose platforms and criteria (niches, hashtags, min metrics).
- Configure export: CSV path and/or Google Sheets (service account JSON and sheet key).
- Optional schedule: cron or interval minutes.
- Optional own accounts metrics collection: set `own_accounts` in config to collect channel/account stats to CSV and Google Sheets.

## Run

One-off run:
```bash
python -m social_viral_parser.cli config.yaml
```

Scheduled (runs as background scheduler until Ctrl+C):
```bash
python -m social_viral_parser.cli config.yaml --schedule
```

Alternative entrypoint:
```bash
python main.py config.yaml
```

## Notes
- Instagram hashtag search requires a Business account and proper permissions in Graph API.
- TikTok connector is optional and may require valid `ms_token` and may be brittle.
- Google Sheets export needs a service account with access to the target spreadsheet.