from datetime import datetime, timezone
import unittest

from scripts.snapshot_delta_universe import build_snapshot, exclusion_reason


def product(symbol: str, description: str, launch_time: str) -> dict[str, object]:
    return {
        "symbol": symbol,
        "description": description,
        "contract_type": "perpetual_futures",
        "state": "live",
        "launch_time": launch_time,
        "underlying_asset": {"symbol": symbol.removesuffix("USD"), "name": description},
        "ui_config": {"tags": []},
    }


class DeltaUniverseTests(unittest.TestCase):
    def test_tokenized_stock_is_excluded(self) -> None:
        item = product("AAPLXUSD", "Apple xStock token perpetual future", "2026-02-01T00:00:00Z")
        self.assertEqual(exclusion_reason(item), "tokenized stock or index")

    def test_gold_token_is_excluded_from_crypto_only_universe(self) -> None:
        item = product("XAUTUSD", "Tether Gold token perpetual future", "2026-04-01T00:00:00Z")
        self.assertEqual(exclusion_reason(item), "gold/silver-linked token")

    def test_recent_crypto_is_kept_in_probation(self) -> None:
        payload = {
            "result": [product("GRAMUSD", "GRAM perpetual future", "2026-07-07T00:00:00Z")]
        }
        snapshot = build_snapshot(
            payload, datetime(2026, 7, 16, tzinfo=timezone.utc)
        )
        self.assertEqual(snapshot["counts"]["crypto_perpetuals"], 1)
        self.assertEqual(snapshot["probation"][0]["symbol"], "GRAMUSD")
        self.assertEqual(snapshot["recent_listings"][0]["symbol"], "GRAMUSD")


if __name__ == "__main__":
    unittest.main()
