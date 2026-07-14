#!/bin/bash
# Docker entrypoint script for Japanese Learning Bot

set -e

echo "🎌 Starting Japanese Learning Bot..."
echo "===================================="

# Check if database exists, if not initialize it
if [ ! -f "/app/data/vocab.db" ]; then
    echo "📊 Initializing database..."
    python -c "from app.database.connection import init_db; init_db()"
    python -m app.utils.load_csv
    echo "✅ Database initialized!"
else
    echo "📊 Database exists, ensuring tables are created..."
    python -c "from app.database.connection import init_db; init_db()"
    echo "✅ Database tables verified!"
fi

echo "🚀 Starting bot..."
exec python run_telegram_bot.py
