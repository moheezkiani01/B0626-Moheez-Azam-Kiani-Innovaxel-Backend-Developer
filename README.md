# Event Registration System API

A simple Event Registration System API built with **Python, FastAPI, and SQLite**.

It supports:

- Create events
- Register users for events
- View events with available seats and total registrations
- Sort events by date
- Filter upcoming events only
- Cancel registrations
- Persistent storage using SQLite
- Protection against duplicate registrations and overbooking

## Tech Stack

- Python 3.10+
- FastAPI
- SQLite
- Uvicorn

## Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

### Health Check

```http
GET /
```

### Create Event

```http
POST /events
```

Request body:

```json
{
  "name": "Python Workshop",
  "total_seats": 50,
  "event_date": "2030-06-01T10:00:00"
}
```

Rules:

- Event name must be unique.
- Total seats must be greater than 0.
- Event date must be in the future.

### View Events

```http
GET /events
```

Optional query parameters:

```text
sort_by_date=true
upcoming_only=true
```

Example:

```http
GET /events?sort_by_date=true&upcoming_only=true
```

Response includes:

- Available seats
- Total registrations

### Register User for Event

```http
POST /registrations
```

Request body:

```json
{
  "user_name": "Ali",
  "event_id": 1
}
```

Rules:

- Cannot register if the event is full.
- Same user cannot register twice for the same event.
- Registration timestamp is stored.
- Concurrent registration requests are protected using a transaction.

### Cancel Registration

```http
DELETE /registrations
```

Request body:

```json
{
  "user_name": "Ali",
  "event_id": 1
}
```

Rules:

- Seat becomes available again.
- Cancelled users do not appear in active registrations.
- Repeated cancel requests are handled safely.

## Design Decisions

### Why SQLite?

SQLite is simple, persistent between runs, and supports transactions. It is suitable for this assessment because authentication and distributed infrastructure are not required.

### How overbooking is prevented

Registration uses a database transaction with:

```sql
BEGIN IMMEDIATE
```

This locks the database for writing during registration. While one registration is being processed, another request cannot update the same event at the same time.

The code checks active registration count inside the same transaction before inserting a new registration.

### How duplicate registration is prevented

The database has a unique constraint:

```sql
UNIQUE(event_id, user_name, status)
```

This prevents the same user from having multiple active registrations for the same event.

### Why cancelled registrations are kept

Cancelled records are not deleted. Their status is changed to:

```text
cancelled
```

This keeps history and makes registration tracking cleaner.

## Example Error Responses

Event already exists:

```json
{
  "detail": "Event name already exists"
}
```

Event full:

```json
{
  "detail": "Event is full"
}
```

Duplicate registration:

```json
{
  "detail": "User is already registered for this event"
}
```

Past event date:

```json
{
  "detail": "Event date must be in the future"
}
```

## Running Tests Manually

Use Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Or use curl/Postman.

## Project Structure

```text
event-registration-api/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── requirements.txt
├── README.md
└── .gitignore
```
