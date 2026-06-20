#!/usr/bin/env python3
"""Thin wrapper around hyag.cli for backward compatibility and skill usage."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from hyag.cli import main

if __name__ == "__main__":
    main()
