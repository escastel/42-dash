import os
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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

    app.state.games_raw: dict[str, Any] = {
        "alpha": [],
        "beta": [],
        "gamma": [],
    }
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

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/games")
    def list_games() -> dict[str, Any]:
        return {
            "data": [],
            "meta": {
                "total": 0,
                "page": 1,
                "pageSize": 20,
                "totalPages": 0
            }
        }

    @app.get("/api/games/{game_id}")
    def get_game(game_id: str) -> dict[str, Any]:
        return {
            "id": game_id,
            "message": "pending implementation",
        }

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