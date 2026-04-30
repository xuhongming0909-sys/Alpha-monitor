"""Data fetch layer structural and correctness tests.

Tests verify:
1. No redundant duplicate files exist
2. No security anti-patterns (verify=False)
3. Normalizers use unified error handling
4. Architecture boundaries respected
"""

from __future__ import annotations

import ast
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TestNoRedundantFiles(unittest.TestCase):
    """tools/ should not contain duplicates of data_fetch logic."""

    def test_fetch_convertible_bond_py_should_not_exist(self) -> None:
        path = ROOT / "tools" / "fetch_convertible_bond.py"
        self.assertFalse(path.exists(), f"Redundant file exists: {path}")

    def test_fetch_dividend_py_should_not_exist(self) -> None:
        path = ROOT / "tools" / "fetch_dividend.py"
        self.assertFalse(path.exists(), f"Redundant file exists: {path}")


class TestSecurityPatterns(unittest.TestCase):
    """No insecure patterns in data fetch code."""

    def test_event_arbitrage_no_verify_false(self) -> None:
        path = ROOT / "data_fetch" / "event_arbitrage" / "fetcher.py"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("verify=False", text, "SSL verify=False found in event_arbitrage fetcher")


class TestNormalizerErrorHandling(unittest.TestCase):
    """Normalizers should use shared error helper instead of inline duplication."""

    def test_market_record_has_create_error_record(self) -> None:
        path = ROOT / "shared" / "bus" / "market_record.py"
        text = path.read_text(encoding="utf-8")
        self.assertIn("def create_error_record", text, "create_error_record helper missing from market_record.py")


class TestArchitectureBoundaries(unittest.TestCase):
    """Layer boundaries: shared/ should not import tools/; data_fetch/ should not import scripts/ or tools/."""

    def test_market_service_no_tools_import(self) -> None:
        path = ROOT / "shared" / "market_service.py"
        text = path.read_text(encoding="utf-8")
        self.assertNotIn("import market_pairs", text, "shared/market_service.py imports tools/market_pairs")
        self.assertNotIn("import premium_history_db", text, "shared/market_service.py imports tools/premium_history_db")

    def test_data_fetch_no_scripts_import(self) -> None:
        """data_fetch/ plugins must only import from shared/ and same-plugin modules."""
        forbidden = ["market_pairs", "premium_history_db", "stock_price_history_db", "subscription_history_db"]
        data_fetch_root = ROOT / "data_fetch"
        for py_file in data_fetch_root.rglob("*.py"):
            text = py_file.read_text(encoding="utf-8")
            for module in forbidden:
                # Allow imports via shared.db (e.g., "from shared.db import premium_history_db")
                # Reject direct imports like "import premium_history_db" or "from market_pairs import ..."
                for line in text.splitlines():
                    stripped = line.strip()
                    if stripped.startswith(f"from shared.db") and module in stripped:
                        continue
                    if stripped.startswith(f"import {module}") or stripped.startswith(f"from {module}"):
                        self.fail(
                            f"{py_file.relative_to(ROOT)} directly imports scripts/{module}: {line.strip()}"
                        )


class TestDataCorrectness(unittest.TestCase):
    """Data fetch outputs should be structurally correct."""

    def test_bus_record_has_required_fields(self) -> None:
        sys.path.insert(0, str(ROOT))
        from shared.bus.market_record import create_market_record, REQUIRED_FIELDS

        record = create_market_record(
            plugin="test",
            market="CN",
            symbol="000001",
            name="测试",
            event_type="test_event",
            quote_time="2026-04-30T12:00:00",
            metrics={"price": 10.0},
            raw={"source": "test"},
            status="ok",
        )
        for field in REQUIRED_FIELDS:
            self.assertIn(field, record, f"Missing required field: {field}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
