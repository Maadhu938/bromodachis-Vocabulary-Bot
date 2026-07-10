# Bromodachis Daily Vocabulary Bot 🇯🇵

A daily **JLPT N5 Japanese vocabulary** bot. Every day at **08:00 (Asia/Kolkata)** it picks a configurable number of new words from a CSV dataset, formats them into a post, and sends it to a **WhatsApp group** through [Evolution API](https://doc.evolution-api.com) (an unofficial WhatsApp bridge).

> **Note on the sender:** Evolution API sends messages from the WhatsApp account you link to it. In the group, posts therefore appear as coming from *your* number/name — there is no separate "bot" identity with this approach.

## How it works

```
┌─────────────┐      ┌──────────────────┐      ┌────────────────────┐
│  vocab-bot  │ ───▶ │  Evolution API   │ ───▶ │  WhatsApp Group    │
│  (FastAPI)  │      │  (WhatsApp bridge)│      │  (Bromodachi's)   │
└─────────────┘      └──────────────────┘      └────────────────────┘
      │                        │
      │ SQLite (vocab.db)     │ PostgreSQL
      │ word tracking          │ instance / session state
      ▼                        ▼
 data/n5.csv ──▶ vocab.db   evolution-postgres
```

1. On startup the bot loads `data/n5.csv` into a local **SQLite** DB (`vocab.db`) — created at image build time by `app/utils/load_csv.py`.
2. **APScheduler** fires `daily_vocabulary_job` every day at 08:00 in the configured timezone (`TIMEZONE`, default `Asia/Kolkata`).
3. The job asks `VocabularyService` for the next N unseen words (`N = WORDS_PER_DAY`), marks them sent (so they are never repeated until the list is exhausted), and formats them via `MessageFormatter`.
4. `WhatsAppMessagingService` POSTs the text to Evolution API (`/message/sendText/{instance}`), which delivers it to `WHATSAPP_GROUP_ID`.

## Features
- **Configurable words/day** — set `WORDS_PER_DAY` (default `5`, currently `3`).
- **Timezone-aware scheduling** — runs at 08:00 in `TIMEZONE` (IST by default).
- **No-duplicate progress tracking** — `sent_words` table records what was sent; `/reset` starts over.
- **Manual + scheduled triggers** — REST endpoints for on-demand send, progress, and reset.
- **Replaceable messaging layer** — `app/messaging/whatsapp.py` is the live sender; `app/messaging/mock.py` is a console-only logger kept for local testing.

## Folder Structure
```
bromodachis-vocab-bot/
├── app/
│   ├── api/
│   │   └── routes.py          # FastAPI endpoints (/today, /send, /progress, /reset)
│   ├── services/
│   │   ├── vocabulary.py      # Word selection + sent-history tracking
│   │   └── formatter.py       # Formats words into the chat message
│   ├── scheduler/
│   │   └── tasks.py           # APScheduler cron job (08:00, configurable TZ)
│   ├── messaging/
│   │   ├── whatsapp.py        # Live sender via Evolution API (v2 payload)
│   │   └── mock.py            # Console logger for local testing
│   ├── database/
│   │   └── connection.py      # SQLAlchemy engine (SQLite vocab.db)
│   ├── models/
│   │   ├── vocabulary.py      # Vocabulary table
│   │   └── sent_words.py      # Sent-history table
│   ├── utils/
│   │   └── load_csv.py        # Loads data/n5.csv → vocab.db (runs at build)
│   └── main.py                # FastAPI app + lifespan (DB init, scheduler)
├── data/
│   └── n5.csv                # Vocabulary dataset (expression,reading,meaning,tags)
├── docker-compose.yml          # evolution-api + postgres + vocab-bot
├── Dockerfile                  # Builds vocab-bot (installs tzdata, loads CSV)
├── .env.example               # Config template (copy to .env)
├── requirements.txt
└── README.md
```

## Prerequisites
- **Docker** + **Docker Compose** v2.
- A WhatsApp account you can link via QR code.

## Setup

1. **Configure environment** — copy the template and fill in real values:
   ```cmd
   copy .env.example .env
   ```
   | Variable | Description |
   | --- | --- |
   | `EVOLUTION_API_KEY` | Global API key for Evolution API (used in the `apikey` header). |
   | `EVOLUTION_INSTANCE_NAME` | Evolution instance name (e.g. `bromodachis`). |
   | `WHATSAPP_GROUP_ID` | Target group id, e.g. `120363xxxxxxxxxx@g.us`. |
   | `WORDS_PER_DAY` | Words sent per batch (default `5`). |
   | `TIMEZONE` | IANA timezone for the 08:00 schedule (e.g. `Asia/Kolkata`). |

2. **Start the stack** (Evolution API + PostgreSQL + bot):
   ```cmd
   docker-compose up -d
   ```
   This pulls `evoapicloud/evolution-api:latest`, a `postgres:16` DB (required by current Evolution API), and builds/runs the bot.

3. **Link your WhatsApp number.** The current Evolution API image does **not** ship the `/manager` web UI, so create the instance and get the QR via the REST API (a small helper is provided):
   ```cmd
   python get_qr.py
   ```
   This writes `qr.png` — open it with your phone (**WhatsApp → Linked Devices → Link a Device**) and scan promptly (QRs expire in ~60s; re-run if needed).

4. **Find the group id.** Once connected, fetch your groups and copy the `id` of the target group into `.env` as `WHATSAPP_GROUP_ID`:
   ```powershell
   # PowerShell
   $h = @{"apikey"="<EVOLUTION_API_KEY>"}
   (Invoke-WebRequest "http://localhost:8080/group/fetchAllGroups/bromodachis?getParticipants=false" -Headers $h).Content
   ```
   Then `docker-compose up -d --force-recreate vocab-bot` to pick up the new value.

## Running
The bot runs as a container and is already scheduled. Useful commands:
```cmd
docker-compose ps                 # see all services
docker-compose logs -f vocab-bot # bot logs (sends, scheduler)
docker-compose logs -f evolution-api
docker-compose down              # stop everything
```

## API Endpoints (bot, port 8000)
- **GET `/today`** — preview the next `WORDS_PER_DAY` words **without** marking them sent.
- **POST `/send`** — pick the next words, mark them sent, format, and push to WhatsApp immediately.
- **GET `/progress`** — `{ total_words, sent_words, remaining_words }`.
- **POST `/reset`** — clear sent history (back to day 1).

## Local development (without WhatsApp)
For working on formatting/logic without Evolution API, the bot can run locally against the `MockMessagingService` (console logger). Set the messaging import to `mock` (or use the `WORDS_PER_DAY`/`TIMEZONE` env vars) and run:
```cmd
python -m venv .venv && .\.venv\Scripts\activate
pip install -r requirements.txt
python -m app.utils.load_csv
set PYTHONPATH=.
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

## Known limitations
- Messages originate from your linked personal WhatsApp number (see note above).
- `vocab.db` is baked into the image at build time from `data/n5.csv`; `/reset` only clears sent-history, it does not reload the CSV.
- Evolution API is an **unofficial** WhatsApp integration — use responsibly and within WhatsApp's terms.
