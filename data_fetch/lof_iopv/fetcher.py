# -*- coding: utf-8 -*-
# AI-SUMMARY: LOF IOPV fetcher - thin wrapper calling source.py
# INDEX section 9.3 file summary index
"""LOF IOPV fetcher. Thin wrapper around source.py for backward compatibility."""

from data_fetch.lof_iopv.source import build_lof_snapshot


def fetch_lof_iopv_snapshot():
    return build_lof_snapshot()
