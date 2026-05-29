"""Tests for strategy/lof_iopv/calc.py - IOPV calculation formula."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from strategy.lof_iopv.calc import to_float, calc_iopv


class TestToFloat(unittest.TestCase):
    def test_valid_number(self):
        self.assertEqual(to_float("3.14"), 3.14)

    def test_none_returns_none(self):
        self.assertIsNone(to_float(None))

    def test_nan_returns_none(self):
        self.assertIsNone(to_float(float("nan")))

    def test_inf_returns_none(self):
        self.assertIsNone(to_float(float("inf")))

    def test_string_returns_none(self):
        self.assertIsNone(to_float("abc"))

    def test_zero_returns_zero(self):
        self.assertEqual(to_float(0), 0.0)


class TestCalcIopv(unittest.TestCase):
    """Test calc_iopv unified formula."""

    def _make_holdings(self, tickers_weights):
        return [{"ticker": t, "weight": w} for t, w in tickers_weights]

    def test_no_holdings_returns_nav_times_fx(self):
        est, status, _ = calc_iopv(
            nav=1.0, holdings=[], stock_ratio=90,
            current_prices={}, nav_date_prices={}, prev_closes={},
            fx_now=7.2, fx_base=7.1,
        )
        self.assertAlmostEqual(est, 1.0 * (7.2 / 7.1), places=4)
        self.assertIn("无持仓", status)

    def test_zero_weight_holdings(self):
        holdings = self._make_holdings([("AAPL", 0)])
        est, status, _ = calc_iopv(
            nav=1.0, holdings=holdings, stock_ratio=90,
            current_prices={}, nav_date_prices={}, prev_closes={},
            fx_now=1.0, fx_base=1.0,
        )
        self.assertIn("权重为零", status)

    def test_single_holding_no_change(self):
        """Price unchanged -> IOPV = NAV * fx_ratio."""
        holdings = self._make_holdings([("AAPL", 100)])
        est, status, details = calc_iopv(
            nav=1.5, holdings=holdings, stock_ratio=80,
            current_prices={"AAPL": 150.0},
            nav_date_prices={"AAPL": 150.0},
            prev_closes={},
            fx_now=7.2, fx_base=7.2,
        )
        self.assertAlmostEqual(est, 1.5, places=4)
        self.assertAlmostEqual(details["weightedRet"], 0.0, places=6)

    def test_single_holding_5pct_up(self):
        """Stock up 5% -> IOPV reflects partial gain based on stock_ratio."""
        holdings = self._make_holdings([("AAPL", 100)])
        est, status, details = calc_iopv(
            nav=1.0, holdings=holdings, stock_ratio=80,
            current_prices={"AAPL": 105.0},
            nav_date_prices={"AAPL": 100.0},
            prev_closes={},
            fx_now=1.0, fx_base=1.0,
        )
        # weighted_ret = 100 * 0.05 = 5.0
        # nav_change = 5.0 * 80 / 100 / 100 = 0.04
        # IOPV = 1.0 * 1.04 * 1.0 = 1.04
        self.assertAlmostEqual(est, 1.04, places=4)

    def test_fx_change_amplifies(self):
        """FX ratio change should multiply the result."""
        holdings = self._make_holdings([("SPY", 100)])
        est, _, details = calc_iopv(
            nav=1.0, holdings=holdings, stock_ratio=90,
            current_prices={"SPY": 100.0},
            nav_date_prices={"SPY": 100.0},
            prev_closes={},
            fx_now=7.3, fx_base=7.0,
        )
        # fx_ratio = 7.3/7.0 = 1.04286
        # nav_change = 0 (no stock change)
        # IOPV = 1.0 * 1.0 * 1.04286 = 1.04286
        self.assertAlmostEqual(est, 1.0 * (7.3 / 7.0), places=4)
        self.assertAlmostEqual(details["fxRatio"], 7.3 / 7.0, places=6)

    def test_two_holdings_weighted(self):
        """Two holdings with different weights and returns."""
        holdings = self._make_holdings([("A", 60), ("B", 40)])
        est, _, details = calc_iopv(
            nav=1.0, holdings=holdings, stock_ratio=100,
            current_prices={"A": 110.0, "B": 90.0},
            nav_date_prices={"A": 100.0, "B": 100.0},
            prev_closes={},
            fx_now=1.0, fx_base=1.0,
        )
        # weighted_ret = 60*0.10 + 40*(-0.10) = 6 - 4 = 2.0
        # nav_change = 2.0 * 100 / 100 / 100 = 0.02
        # IOPV = 1.0 * 1.02 = 1.02
        self.assertAlmostEqual(est, 1.02, places=4)
        self.assertAlmostEqual(details["weightedRet"], 2.0, places=4)

    def test_no_price_returns_none(self):
        """No price data -> returns None (cannot estimate IOPV)."""
        holdings = self._make_holdings([("AAPL", 100)])
        est, status, _ = calc_iopv(
            nav=2.0, holdings=holdings, stock_ratio=90,
            current_prices={}, nav_date_prices={}, prev_closes={},
            fx_now=7.0, fx_base=7.0,
        )
        self.assertIsNone(est)
        self.assertIn("无股价", status)
    def test_prev_close_fallback(self):
        """When nav_date_prices missing, use prev_closes as fallback."""
        holdings = self._make_holdings([("AAPL", 100)])
        est, _, details = calc_iopv(
            nav=1.0, holdings=holdings, stock_ratio=80,
            current_prices={"AAPL": 110.0},
            nav_date_prices={},
            prev_closes={"AAPL": 100.0},
            fx_now=1.0, fx_base=1.0,
        )
        # Uses prev_close: ret = 110/100 - 1 = 0.10
        # weighted_ret = 100 * 0.10 = 10
        # nav_change = 10 * 80 / 100 / 100 = 0.08
        self.assertAlmostEqual(est, 1.08, places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)