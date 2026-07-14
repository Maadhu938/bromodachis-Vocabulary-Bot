#!/usr/bin/env python3
"""
Simple script to run the Telegram Japanese Learning Bot
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.telegram_bot import main

if __name__ == "__main__":
    print("🎌 Starting Bromodachis Japanese Learning Bot...")
    print("=" * 50)
    main()
