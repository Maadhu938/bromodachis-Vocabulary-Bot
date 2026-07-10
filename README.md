# Bromodachis Daily Vocabulary Bot 🇯🇵

A daily JLPT N5 vocabulary bot built with Python, FastAPI, and APScheduler. It automatically picks 5 new Japanese vocabulary words from your CSV database every day and prepares a formatted message ready for sending to your group chat.

## Features
- **Daily Vocabulary**: Sends 5 JLPT N5 vocabulary words every day at 8:00 AM.
- **Smart Progress Tracking**: Uses SQLite to keep track of which words have already been sent, ensuring no duplicates until the entire list is exhausted.
- **Ready for WhatsApp/Telegram**: Designed with a replaceable `MockMessagingService` layer. You can easily plug in a WhatsApp Cloud API, Evolution API, or Telegram Bot implementation.
- **FastAPI Endpoints**: Includes REST APIs to manually trigger messages, check progress, and reset the list.

## Folder Structure
```
bromodachis-vocab-bot/
│
├── app/
│   ├── api/
│   │   └── routes.py         # FastAPI endpoints
│   ├── services/
│   │   ├── vocabulary.py     # Core logic for picking words and tracking sent history
│   │   └── formatter.py      # Formats the 5 words into the beautiful chat message
│   ├── scheduler/
│   │   └── tasks.py          # APScheduler cron jobs
│   ├── messaging/
│   │   └── mock.py           # Mock messaging layer (Replace with WhatsApp/Telegram)
│   ├── database/
│   │   └── connection.py     # SQLite DB setup
│   ├── models/
│   │   ├── vocabulary.py     # Vocabulary table
│   │   └── sent_words.py     # Sent history table
│   ├── utils/
│   │   └── load_csv.py       # Script to load CSV into SQLite
│   └── main.py               # FastAPI application entrypoint
│
├── data/
│   └── n5.csv                # The vocabulary dataset
│
├── requirements.txt
└── README.md
```

## Installation

1. Create a virtual environment and activate it:
   ```cmd
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. Install the requirements:
   ```cmd
   pip install -r requirements.txt
   ```

## Setup & Configuration
1. Place your CSV file in `data/n5.csv`. The CSV should have headers: `expression,reading,meaning,tags`.
2. Load the CSV into the database:
   ```cmd
   python app/utils/load_csv.py
   ```
   *This creates `vocab.db` in the root folder and loads the words.*

## Running the Bot

Run the FastAPI server using Uvicorn. The APScheduler background job starts automatically and is scheduled for 8:00 AM daily.

```cmd
set PYTHONPATH=.
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## API Endpoints

- **GET `/today`** - Get the 5 words for today without marking them as sent.
- **POST `/send`** - Force trigger the bot to pick 5 words, mark them as sent, format the message, and push it to the messaging service immediately.
- **GET `/progress`** - Get statistics on how many words have been sent and how many are remaining.
- **POST `/reset`** - Reset the bot's progress back to day 1.

## Replacing the Messaging Layer
Currently, the bot uses `MockMessagingService` located in `app/messaging/mock.py`, which simply prints the message to the console log. 

To connect this to WhatsApp or Telegram, edit `app/messaging/mock.py` (or create a new file) and implement your API calls inside the `send_message(self, message: str)` method.
