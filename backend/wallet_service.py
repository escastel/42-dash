from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
import threading
from typing import Any


MONEY_QUANT = Decimal("0.01")


@dataclass
class WalletError(Exception):
    status_code: int
    code: str
    message: str
    details: list[Any] | None = None


@dataclass
class TransactionRecord:
    payload_hash: str
    response: dict[str, Any]


@dataclass
class BetRecord:
    amount: Decimal
    settled: bool = False
    rolled_back: bool = False


class WalletService:
    def __init__(self, initial_balance: Decimal) -> None:
        self._lock = threading.Lock()
        self._balance = self._quantize(initial_balance)
        self._transactions: dict[str, TransactionRecord] = {}
        self._bets: dict[str, BetRecord] = {}

    def get_balance(self) -> Decimal:
        with self._lock:
            return self._balance

    def bet(self, transaction_id: str, amount: Decimal) -> dict[str, Any]:
        amount = self._validate_positive_amount(amount)
        payload_hash = self._build_payload_hash(
            {
                "op": "bet",
                "transactionId": transaction_id,
                "amount": self._money_str(amount),
            }
        )

        with self._lock:
            replay = self._validate_idempotency(transaction_id, payload_hash)
            if replay is not None:
                return replay

            if amount > self._balance:
                raise WalletError(
                    status_code=409,
                    code="INSUFFICIENT_FUNDS",
                    message="Insufficient funds for bet",
                    details=[],
                )

            self._balance = self._quantize(self._balance - amount)
            self._bets[transaction_id] = BetRecord(amount=amount)

            response = {
                "transactionId": transaction_id,
                "balance": float(self._balance),
            }
            self._transactions[transaction_id] = TransactionRecord(
                payload_hash=payload_hash,
                response=response,
            )
            return response

    def settle(
        self,
        transaction_id: str,
        bet_transaction_id: str,
        amount: Decimal,
    ) -> dict[str, Any]:
        amount = self._validate_non_negative_amount(amount)
        payload_hash = self._build_payload_hash(
            {
                "op": "settle",
                "transactionId": transaction_id,
                "betTransactionId": bet_transaction_id,
                "amount": self._money_str(amount),
            }
        )

        with self._lock:
            replay = self._validate_idempotency(transaction_id, payload_hash)
            if replay is not None:
                return replay

            bet = self._bets.get(bet_transaction_id)
            if bet is None:
                raise WalletError(
                    status_code=404,
                    code="BET_NOT_FOUND",
                    message="Referenced bet transaction does not exist",
                    details=[],
                )

            if bet.settled:
                raise WalletError(
                    status_code=409,
                    code="BET_ALREADY_SETTLED",
                    message="Bet already settled",
                    details=[],
                )

            if bet.rolled_back:
                raise WalletError(
                    status_code=409,
                    code="BET_ALREADY_ROLLED_BACK",
                    message="Bet already rolled back",
                    details=[],
                )

            self._balance = self._quantize(self._balance + amount)
            bet.settled = True

            response = {
                "transactionId": transaction_id,
                "betTransactionId": bet_transaction_id,
                "balance": float(self._balance),
            }
            self._transactions[transaction_id] = TransactionRecord(
                payload_hash=payload_hash,
                response=response,
            )
            return response

    def rollback(self, transaction_id: str, bet_transaction_id: str) -> dict[str, Any]:
        payload_hash = self._build_payload_hash(
            {
                "op": "rollback",
                "transactionId": transaction_id,
                "betTransactionId": bet_transaction_id,
            }
        )

        with self._lock:
            replay = self._validate_idempotency(transaction_id, payload_hash)
            if replay is not None:
                return replay

            bet = self._bets.get(bet_transaction_id)
            if bet is None:
                raise WalletError(
                    status_code=404,
                    code="BET_NOT_FOUND",
                    message="Referenced bet transaction does not exist",
                    details=[],
                )

            if bet.settled:
                raise WalletError(
                    status_code=409,
                    code="BET_ALREADY_SETTLED",
                    message="Settled bets are immutable",
                    details=[],
                )

            if bet.rolled_back:
                raise WalletError(
                    status_code=409,
                    code="BET_ALREADY_ROLLED_BACK",
                    message="Bet already rolled back",
                    details=[],
                )

            self._balance = self._quantize(self._balance + bet.amount)
            bet.rolled_back = True

            response = {
                "transactionId": transaction_id,
                "betTransactionId": bet_transaction_id,
                "balance": float(self._balance),
            }
            self._transactions[transaction_id] = TransactionRecord(
                payload_hash=payload_hash,
                response=response,
            )
            return response

    def _validate_idempotency(
        self,
        transaction_id: str,
        payload_hash: str,
    ) -> dict[str, Any] | None:
        existing = self._transactions.get(transaction_id)
        if existing is None:
            return None

        if existing.payload_hash != payload_hash:
            raise WalletError(
                status_code=409,
                code="IDEMPOTENCY_CONFLICT",
                message="transactionId already used with different payload",
                details=[],
            )

        return existing.response

    @staticmethod
    def _build_payload_hash(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _quantize(value: Decimal) -> Decimal:
        return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)

    @staticmethod
    def _money_str(value: Decimal) -> str:
        return str(value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP))

    def _validate_positive_amount(self, amount: Decimal) -> Decimal:
        amount = self._quantize(amount)
        if amount <= Decimal("0.00"):
            raise WalletError(
                status_code=400,
                code="INVALID_AMOUNT",
                message="amount must be greater than 0",
                details=[],
            )
        return amount

    def _validate_non_negative_amount(self, amount: Decimal) -> Decimal:
        amount = self._quantize(amount)
        if amount < Decimal("0.00"):
            raise WalletError(
                status_code=400,
                code="INVALID_AMOUNT",
                message="amount must be greater than or equal to 0",
                details=[],
            )
        return amount
