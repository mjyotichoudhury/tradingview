from pathlib import Path
import unittest

from scripts.validate_crypto_strategy import validate


ROOT = Path(__file__).resolve().parents[1]
STRATEGY = ROOT / "strategies" / "crypto_cycle_smart_hold.pine"


class CryptoStrategyContractTests(unittest.TestCase):
    def test_repository_strategy_passes_contract(self) -> None:
        self.assertEqual(validate(STRATEGY.read_text(encoding="utf-8")), [])

    def test_same_bar_processing_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace(
            "process_orders_on_close = false", "process_orders_on_close = true"
        )
        self.assertTrue(any("same-bar" in failure for failure in validate(source)))

    def test_missing_confirmed_weekly_offset_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace("close[1]", "close", 1)
        self.assertTrue(any("weekly data" in failure for failure in validate(source)))

    def test_unpaired_higher_timeframe_request_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace(
            "lookahead = barmerge.lookahead_on", "lookahead = barmerge.lookahead_off", 1
        )
        failures = validate(source)
        self.assertTrue(any("lookahead" in failure for failure in failures))

    def test_incorrect_cost_model_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace(
            "commission_value = 0.1", "commission_value = 0.0"
        )
        self.assertTrue(any("commission" in failure for failure in validate(source)))

    def test_aggressive_default_position_size_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace(
            'input.float(30.0, "Position size (% of equity)"',
            'input.float(95.0, "Position size (% of equity)"',
        )
        self.assertTrue(any("drawdown-compatible" in failure for failure in validate(source)))


if __name__ == "__main__":
    unittest.main()
