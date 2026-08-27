#!/usr/bin/env python3
"""Run the reproducible synthetic Phase 1 pilot without external services."""
from __future__ import annotations

import json

from gov_platform.phase1_demo import run_phase1_demo


if __name__ == "__main__":
    print(json.dumps(run_phase1_demo(), indent=2, sort_keys=True, default=str))
