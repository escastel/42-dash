import os
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from normalize_data import find_game_by_id, normalize_all_games, query_games


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_FILES = [
    BASE_DIR / "data" / "provider-alpha.json",
    BASE_DIR / "data" / "provider-beta.json",
    BASE_DIR / "data" / "provider-gamma.json",
]


def parse_data_files() -> list[Path]:
    raw = os.getenv("DATA_FILES", "").strip()
    if not raw:
        return DEFAULT_DATA_FILES
    return [Path(p.strip()) for p in raw.split(",") if p.strip()]


def create_app() -> FastAPI:
    app = FastAPI(
        title="QtechDash Backend",
        version="0.1.0",
        description="Game Aggregator API",
    )

    # CORS abierto para facilitar integración FE durante el reto
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.games_raw = {
        "alpha": [],
        "beta": [],
        "gamma": [],
    }
    app.state.games = []
    app.state.launch_secret = os.getenv("LAUNCH_SECRET", "default-secret-change-me")

    @app.on_event("startup")
    def load_provider_files() -> None:
        files = parse_data_files()
        labels = ["alpha", "beta", "gamma"]

        for idx, path in enumerate(files):
            if idx >= len(labels):
                break
            label = labels[idx]
            try:
                with path.open("r", encoding="utf-8") as f:
                    app.state.games_raw[label] = json.load(f)
            except FileNotFoundError:
                app.state.games_raw[label] = []
            except json.JSONDecodeError:
                app.state.games_raw[label] = []

        app.state.games = normalize_all_games(app.state.games_raw)

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/games")
    def list_games(
        search: str | None = Query(default=None),
        name: str | None = Query(default=None),
        provider: str | None = Query(default=None),
        category: str | None = Query(default=None),
        enabled: str | None = Query(default=None),
        sort: str = Query(default="name"),
        order: str = Query(default="asc"),
        page: int = Query(default=1, ge=1),
        pageSize: int = Query(default=20, ge=1),
    ) -> dict[str, Any]:
        return query_games(
            app.state.games,
            search=search,
            name=name,
            provider=provider,
            category=category,
            enabled=enabled,
            sort=sort,
            order=order,
            page=page,
            page_size=pageSize,
        )

    @app.get("/api/games/{game_id}", response_model=None)
    def get_game(game_id: str) -> dict[str, Any] | JSONResponse:
        game = find_game_by_id(app.state.games, game_id)
        if game is not None:
            return game

        return JSONResponse(
            status_code=404,
            content={
                "code": "NOT_FOUND",
                "message": f"Game with id '{game_id}' was not found",
                "details": [],
            },
        )

    @app.post("/api/launch")
    def launch_game(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "message": "pending implementation",
            "received": payload,
        }

    app.state.wallet_balance = float(os.getenv("INITIAL_BALANCE", "10000"))

    @app.get("/api/wallet/balance")
    def get_wallet_balance() -> dict[str, float]:
        return {
            "balance": round(float(app.state.wallet_balance), 2),
        }

    return app


app = create_app()