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
# Use webhook mode for Render Web Service (free tier)
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
