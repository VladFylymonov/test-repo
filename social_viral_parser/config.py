from __future__ import annotations
import yaml
from pathlib import Path
from pydantic import ValidationError
from .models import RunConfig


def load_config(path: str | Path) -> RunConfig:
	path = Path(path)
	with path.open("r", encoding="utf-8") as f:
		data = yaml.safe_load(f)
	try:
		return RunConfig.model_validate(data)
	except ValidationError as exc:
		raise SystemExit(f"Invalid config: {exc}")