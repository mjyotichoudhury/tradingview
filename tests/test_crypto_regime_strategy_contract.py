from pathlib import Path
import unittest

from scripts.validate_crypto_regime_strategy import validate


ROOT = Path(__file__).resolve().parents[1]
STRATEGY = ROOT / "strategies" / "crypto_regime_compounder.pine"


class CryptoRegimeStrategyContractTests(unittest.TestCase):
    def test_repository_strategy_passes_contract(self) -> None:
        self.assertEqual(validate(STRATEGY.read_text(encoding="utf-8")), [])

    def test_same_bar_processing_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace(
            "process_orders_on_close = false", "process_orders_on_close = true"
        )
        self.assertTrue(any("same-bar" in failure for failure in validate(source)))

    def test_unconfirmed_weekly_value_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace("close[1]", "close", 1)
        self.assertTrue(any("weekly close" in failure for failure in validate(source)))

    def test_missing_short_disable_control_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace("allowShort", "shortControl")
        self.assertTrue(any("spot" in failure for failure in validate(source)))

    def test_missing_risk_sizing_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace(
            "riskSizedQuantity", "distanceQuantity"
        )
        self.assertTrue(any("risk sizing" in failure for failure in validate(source)))

    def test_missing_new_listing_history_gate_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace(
            "minimumHistoryBars", "warmupBars"
        )
        self.assertTrue(any("history gate" in failure for failure in validate(source)))


if __name__ == "__main__":
    unittest.main()
