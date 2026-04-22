from __future__ import annotations

from typing import Any


CATEGORY_MAP_BETA = {
	"SL": "slots",
	"LV": "live",
	"TB": "table",
	"IN": "instant",
	"JP": "jackpot",
}


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
	tags = item.get("features", [])
	if not isinstance(tags, list):
		tags = []

	return {
		"id": str(item.get("gameId", "")),
		"name": str(item.get("title", "")),
		"provider": str(item.get("studio", "")),
		"category": str(item.get("type", "")).lower(),
		"rtp": float(item.get("returnToPlayer", 0.0)),
		"volatility": str(item.get("variance", "")).lower(),
		"enabled": bool(item.get("active", False)),
		"releasedAt": str(item.get("launchDate", "")),
		"tags": [str(tag) for tag in tags],
		"thumbnailUrl": str(item.get("thumbnail", "")),
	}


def normalize_beta(item: dict[str, Any]) -> dict[str, Any]:
	category_code = str(item.get("gameCategory", "")).upper()
	raw_tags = str(item.get("tagList", "")).strip()
	tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()] if raw_tags else []

	return {
		"id": str(item.get("gameCode", "")),
		"name": str(item.get("gameName", "")),
		"provider": str(item.get("providerName", "")),
		"category": CATEGORY_MAP_BETA.get(category_code, category_code.lower()),
		"rtp": float(item.get("rtpValue", 0.0)),
		"volatility": str(item.get("riskLevel", "")).lower(),
		"enabled": int(item.get("isEnabled", 0)) == 1,
		"releasedAt": str(item.get("releaseDate", "")),
		"tags": tags,
		"thumbnailUrl": str(item.get("imageUrl", "")),
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
		"name": str(attrs.get("displayName", "")),
		"provider": str(provider.get("label", "")),
		"category": str(classification.get("category", "")).lower(),
		"rtp": float(metrics.get("rtp", 0.0)) * 100.0,
		"volatility": str(classification.get("volatility", "")).lower(),
		"enabled": bool(status.get("enabled", False)),
		"releasedAt": str(status.get("released", "")),
		"tags": tags,
		"thumbnailUrl": str(media.get("thumbnailUrl", "")),
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
