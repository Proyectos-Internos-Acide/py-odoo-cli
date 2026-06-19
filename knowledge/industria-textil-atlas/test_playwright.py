#!/usr/bin/env python3
import sys

try:
    import playwright
    print(f"Playwright is installed. Version: {playwright.__version__}")
except ImportError:
    print("Playwright is NOT installed in this environment.")
