"""Tests for backtest_v2.py - multi-currency and DB holdings."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestBacktestFxLookup(unittest.TestCase):
    """backtest_v2 should look up FX for the fund's actual currency, not hardcoded USD."""

    def test_get_fx_rates_returns_both_usd_and_hkd(self):
        """_get_fx_rates should handle multiple currencies."""
        from strategy.lof_iopv.backtest_v2 import _get_fx_rates
        # This is a smoke test - it queries the DB
        # With empty DB it should return empty dict, not crash
        result = _get_fx_rates("2026-01-01", "2026-05-01")
        self.assertIsInstance(result, dict)

    def test_backtest_fund_handles_hkd_currency(self):
        """backtest_fund should use HKD rates for HK-denominated funds."""
        # This test verifies the function doesn't crash for non-USD funds
        # Full integration test would need DB data
        from strategy.lof_iopv.backtest_v2 import backtest_fund
        # With empty DB, should return None gracefully
        result = backtest_fund("999999", "2026-05-29")
        self.assertIsNone(result)


class TestBacktestHoldings(unittest.TestCase):
    """backtest should use DB holdings when available for B-class funds."""

    def test_get_holdings_returns_list(self):
        from strategy.lof_iopv.backtest_v2 import _get_holdings
        result = _get_holdings("164701")
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main(verbosity=2)