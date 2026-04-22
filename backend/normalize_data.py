from __future__ import annotations

from typing import Any
from datetime import datetime


CATEGORY_MAP_BETA = {
	"SL": "slots",
	"LV": "live",
	"TB": "table",
	"IN": "instant",
	"JP": "jackpot",
}

VOLATILITY_MAP_BETA = {
	"LOW": "low",
	"MED": "medium",
	"HIGH": "high",
}


def _get(item: dict[str, Any], *keys: str, default: Any = "") -> Any:
	for key in keys:
		if key in item:
			return item.get(key)
	return default


def normalize_date_iso(value: str) -> str:
	# Keeps only the date portion for canonical `releasedAt` (YYYY-MM-DD).
	if not value:
		return ""
	value = value.strip()
	try:
		return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
	except ValueError:
		return value.split("T", 1)[0]


def normalize_date_ddmmyyyy(value: str) -> str:
	if not value:
		return ""
	value = value.strip()
	try:
		return datetime.strptime(value, "%d/%m/%Y").date().isoformat()
	except ValueError:
		return value


def parse_bool(value: str | None, default: bool = True) -> bool:
	if value is None:
		return default

	normalized = value.strip().lower()
	if normalized in {"true", "1", "yes", "y", "on"}:
		return True
	if normalized in {"false", "0", "no", "n", "off"}:
		return False
	return default


def normalize_alpha(item: dict[str, Any]) -> dict[str, Any]:
	tags = _get(item, "features", default=[])
	if not isinstance(tags, list):
		tags = []

	return {
		"id": str(_get(item, "gameId", "game_id", default="")),
		"name": str(_get(item, "title", default="")),
		"provider": str(_get(item, "studio", default="")),
		"category": str(_get(item, "type", default="")).lower(),
		"rtp": float(_get(item, "returnToPlayer", "return_to_player", default=0.0)),
		"volatility": str(_get(item, "variance", default="")).lower(),
		"enabled": bool(_get(item, "active", default=False)),
		"releasedAt": normalize_date_iso(str(_get(item, "launchDate", "launch_date", default=""))),
		"tags": [str(tag) for tag in tags],
		"thumbnailUrl": str(_get(item, "thumbnail", default="")),
	}


def normalize_beta(item: dict[str, Any]) -> dict[str, Any]:
	category_code = str(_get(item, "gameCategory", "game_category", default="")).upper()
	risk_level = str(_get(item, "riskLevel", "risk_level", default="")).upper()
	raw_tags = str(_get(item, "tagList", "tag_list", default="")).strip()
	tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()] if raw_tags else []

	return {
		"id": str(_get(item, "gameCode", "game_code", default="")),
		"name": str(_get(item, "gameName", "game_name", default="")),
		"provider": str(_get(item, "providerName", "provider_name", default="")),
		"category": CATEGORY_MAP_BETA.get(category_code, category_code.lower()),
		"rtp": float(_get(item, "rtpValue", "rtp_value", default=0.0)),
		"volatility": VOLATILITY_MAP_BETA.get(risk_level, risk_level.lower()),
		"enabled": int(_get(item, "isEnabled", "is_enabled", default=0)) == 1,
		"releasedAt": normalize_date_ddmmyyyy(str(_get(item, "releaseDate", "release_date", default=""))),
		"tags": tags,
		"thumbnailUrl": str(_get(item, "imageUrl", "image_url", default="")),
	}


def normalize_gamma(item: dict[str, Any]) -> dict[str, Any]:
	data = item.get("data", {})
	attrs = data.get("attributes", {})
	provider = attrs.get("provider", {})
	classification = attrs.get("classification", {})
	metrics = attrs.get("metrics", {})
	status = attrs.get("status", {})
	media = attrs.get("media", {})
	raw_tags = attrs.get("tags", [])
	tags: list[str] = []
	if isinstance(raw_tags, list):
		for tag in raw_tags:
			if isinstance(tag, dict):
				slug = tag.get("slug")
				if slug:
					tags.append(str(slug))

	return {
		"id": str(data.get("id", "")),
		"name": str(_get(attrs, "displayName", "display_name", default="")),
		"provider": str(provider.get("label", "")),
		"category": str(classification.get("category", "")).lower(),
		"rtp": float(metrics.get("rtp", 0.0)) * 100.0,
		"volatility": str(classification.get("volatility", "")).lower(),
		"enabled": bool(status.get("enabled", False)),
		"releasedAt": normalize_date_iso(str(status.get("released", ""))),
		"tags": tags,
		"thumbnailUrl": str(_get(media, "thumbnailUrl", "thumbnail_url", default="")),
	}


def normalize_all_games(games_raw: dict[str, Any]) -> list[dict[str, Any]]:
	output: list[dict[str, Any]] = []

	for item in games_raw.get("alpha", []):
		output.append(normalize_alpha(item))

	for item in games_raw.get("beta", []):
		output.append(normalize_beta(item))

	for item in games_raw.get("gamma", []):
		output.append(normalize_gamma(item))

	cleaned: list[dict[str, Any]] = []
	for game in output:
		if not game.get("id") or not game.get("name"):
			continue
		cleaned.append(game)

	return cleaned


def query_games(
	games: list[dict[str, Any]],
	*,
	search: str | None,
	name: str | None,
	provider: str | None,
	category: str | None,
	enabled: str | None,
	sort: str,
	order: str,
	page: int,
	page_size: int,
) -> dict[str, Any]:
	query_name = (search or name or "").strip().lower()
	query_provider = (provider or "").strip().lower()
	query_category = (category or "").strip().lower()
	query_enabled = parse_bool(enabled, default=True)

	filtered = [game for game in games if game.get("enabled") == query_enabled]

	if query_provider:
		filtered = [
			game
			for game in filtered
			if str(game.get("provider", "")).strip().lower() == query_provider
		]

	if query_category:
		filtered = [
			game
			for game in filtered
			if str(game.get("category", "")).strip().lower() == query_category
		]

	if query_name:
		filtered = [
			game
			for game in filtered
			if query_name in str(game.get("name", "")).strip().lower()
		]

	sort_key = sort.strip().lower()
	if sort_key not in {"name", "rtp"}:
		sort_key = "name"

	reverse = order.strip().lower() == "desc"
	if sort_key == "rtp":
		filtered.sort(key=lambda game: float(game.get("rtp", 0.0)), reverse=reverse)
	else:
		filtered.sort(
			key=lambda game: str(game.get("name", "")).lower(),
			reverse=reverse,
		)

	total = len(filtered)
	total_pages = (total + page_size - 1) // page_size if total > 0 else 0

	start = (page - 1) * page_size
	end = start + page_size
	page_items = filtered[start:end]

	return {
		"data": page_items,
		"meta": {
			"total": total,
			"page": page,
			"pageSize": page_size,
			"totalPages": total_pages,
		},
	}


def find_game_by_id(games: list[dict[str, Any]], game_id: str) -> dict[str, Any] | None:
	for game in games:
		if str(game.get("id")) == game_id:
			return game
	return None
