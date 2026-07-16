from pathlib import Path
import unittest

from scripts.validate_strategy import validate


ROOT = Path(__file__).resolve().parents[1]
STRATEGY = ROOT / "strategies" / "gold_trend_breakout.pine"


class StrategyContractTests(unittest.TestCase):
    def test_repository_strategy_passes_contract(self) -> None:
        self.assertEqual(validate(STRATEGY.read_text(encoding="utf-8")), [])

    def test_future_daily_data_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace(
            "ta.ema(close, trendLength)[1]", "ta.ema(close, trendLength)"
        )
        failures = validate(source)
        self.assertTrue(any("confirmed value" in failure for failure in failures))

    def test_same_bar_processing_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8").replace(
            "process_orders_on_close = false", "process_orders_on_close = true"
        )
        failures = validate(source)
        self.assertTrue(any("same-bar" in failure for failure in failures))

    def test_ineffective_strategy_alertcondition_is_rejected(self) -> None:
        source = STRATEGY.read_text(encoding="utf-8") + "\nalertcondition(true)\n"
        failures = validate(source)
        self.assertTrue(any("alertcondition" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
