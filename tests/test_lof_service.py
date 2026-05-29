"""Tests for service.py - FX fallback, monitor pools, DB context."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


class TestMonitorPools(unittest.TestCase):
    """Test _monitor_pools threshold logic."""

    def test_no_premium_returns_false(self):
        from strategy.lof_iopv.service import _monitor_pools
        lim, unlim = _monitor_pools({"premiumRate": None})
        self.assertFalse(lim)
        self.assertFalse(unlim)

    def test_premium_03_no_monitor(self):
        from strategy.lof_iopv.service import _monitor_pools
        lim, unlim = _monitor_pools({"premiumRate": 0.3})
        self.assertFalse(lim)
        self.assertFalse(unlim)

    def test_premium_06_limited_only(self):
        from strategy.lof_iopv.service import _monitor_pools
        lim, unlim = _monitor_pools({"premiumRate": 0.6})
        self.assertTrue(lim)
        self.assertFalse(unlim)

    def test_premium_15_both(self):
        from strategy.lof_iopv.service import _monitor_pools
        lim, unlim = _monitor_pools({"premiumRate": 1.5})
        self.assertTrue(lim)
        self.assertTrue(unlim)

    def test_negative_premium_also_monitors(self):
        from strategy.lof_iopv.service import _monitor_pools
        lim, unlim = _monitor_pools({"premiumRate": -2.0})
        self.assertTrue(lim)
        self.assertTrue(unlim)


class TestGetFxBaseFromDb(unittest.TestCase):
    """Test _get_fx_base_from_db date range safety."""

    def test_returns_none_for_missing_currency(self):
        from strategy.lof_iopv.service import _get_fx_base_from_db
        result = _get_fx_base_from_db("USD", "2099-01-01")
        # Should return None or a float, not crash
        self.assertTrue(result is None or isinstance(result, float))

    def test_cny_returns_1(self):
        from strategy.lof_iopv.service import _get_fx_base_from_db
        result = _get_fx_base_from_db("CNY", "2026-01-01")
        self.assertEqual(result, 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)