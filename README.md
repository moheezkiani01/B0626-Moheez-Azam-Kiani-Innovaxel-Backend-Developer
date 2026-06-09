# Event Registration System API

A simple Event Registration System built with **FastAPI**, **SQLite**, and a basic **HTML/CSS/JavaScript frontend**.

This project allows users to create events, register users for events, cancel registrations, and track available seats.

---

## Project Overview

The system supports:

- Creating events
- Registering users for events
- Viewing all events
- Sorting events by date
- Filtering upcoming events only
- Cancelling registrations
- Tracking available seats
- Preventing duplicate registrations
- Preventing overbooking
- Persisting data between runs using SQLite

---

## Tech Stack

- Python
- FastAPI
- SQLite
- HTML
- CSS
- JavaScript
- Uvicorn

---

## Project Structure

```text
event-registration-api/
├── run.py
├── requirements.txt
├── README.md
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── script.js
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_LINK
```

```bash
cd event-registration-api
```

---

### 2. Create Virtual Environment

```bash
python -m venv myenv
```

---

### 3. Activate Virtual Environment

For Windows:

```bash
myenv\Scripts\activate
```

For macOS/Linux:

```bash
source myenv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Project

### Option 1: Run with Command

```bash
uvicorn app.main:app
```

Then open:

```text
http://127.0.0.1:8000
```

---

### Option 2: Run by Clicking Run in VS Code

Open:

```text
run.py
```

Click the **Run** button.

The browser will open automatically at:

```text
http://127.0.0.1:8000
```

---

## Frontend

The project includes a simple frontend.

Frontend URL:

```text
http://127.0.0.1:8000
```

From the frontend, users can:

- Create an event
- Register a user for an event
- Cancel registration
- View all events
- Check available seats
- Sort events by date
- Filter upcoming events only

---

## API Documentation

FastAPI provides automatic Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

---

## Health Check

```http
GET /health
```

Response:

```json
{
  "message": "Event Registration System API is running"
}
```

---

## Create Event

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

Successful response:

```json
{
  "id": 1,
  "name": "Python Workshop",
  "total_seats": 50,
  "event_date": "2030-06-01T10:00:00+00:00"
}
```

Possible errors:

```json
{
  "detail": "Event name already exists"
}
```

```json
{
  "detail": "Event date must be in the future"
}
```

---

## View Events

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

Response example:

```json
[
  {
    "id": 1,
    "name": "Python Workshop",
    "total_seats": 50,
    "event_date": "2030-06-01T10:00:00+00:00",
    "available_seats": 49,
    "total_registrations": 1
  }
]
```

This endpoint displays:

- Event ID
- Event name
- Event date
- Total seats
- Total active registrations
- Available seats

Available seats are calculated using:

```text
Available Seats = Total Seats - Active Registrations
```

---

## Register User for Event

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

- Event must exist.
- Event must not be full.
- Same user cannot register twice for the same active event.
- Registration timestamp is stored.
- Race condition protection is applied.

Successful response:

```json
{
  "registration_id": 1,
  "event_id": 1,
  "user_name": "Ali",
  "status": "active",
  "registered_at": "2030-01-01T10:00:00+00:00"
}
```

Possible errors:

```json
{
  "detail": "Event not found"
}
```

```json
{
  "detail": "Event is full"
}
```

```json
{
  "detail": "User is already registered for this event"
}
```

---

## Cancel Registration

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

- Only active registrations can be cancelled.
- Cancelled users are not counted in active registrations.
- Seat becomes available again after cancellation.
- Registration history is kept.

Successful response:

```json
{
  "message": "Registration cancelled successfully",
  "event_id": 1,
  "user_name": "Ali"
}
```

Possible error:

```json
{
  "detail": "Active registration not found"
}
```

---

## Database Design

The project uses SQLite.

Database file:

```text
events.db
```

This file is created automatically when the project runs.

---

## Events Table

Stores event information.

Fields:

- `id`
- `name`
- `total_seats`
- `event_date`
- `created_at`

Important rules:

- `name` is unique.
- `total_seats` must be greater than 0.

---

## Registrations Table

Stores event registration records.

Fields:

- `id`
- `event_id`
- `user_name`
- `status`
- `registered_at`
- `cancelled_at`

Registration status can be:

```text
active
cancelled
```

Cancelled registrations are not deleted. They are marked as cancelled so that history is preserved.

---

## Race Condition and Overbooking Prevention

The hidden tricky requirement is to prevent overbooking when multiple users register at the same time.

This project handles that using SQLite transactions:

```python
cursor.execute("BEGIN IMMEDIATE")
```

This locks the database for writing during the registration process.

The system checks available seats and inserts the registration inside the same transaction. This prevents two users from taking the same last seat at the same time.

---

## Duplicate Registration Prevention

The system prevents the same user from registering twice for the same active event using a unique index:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS unique_active_registration
ON registrations(event_id, user_name)
WHERE status = 'active'
```

This allows a user to register again only after their previous registration has been cancelled.

---

## Validation Rules

The system validates:

- Empty event names
- Duplicate event names
- Negative or zero seats
- Past event dates
- Empty user names
- Invalid event IDs
- Duplicate active registrations
- Full events
- Cancelling non-existing active registrations

---

## Error Handling

The API returns clear error messages.

Examples:

```json
{
  "detail": "Event is full"
}
```

```json
{
  "detail": "Event name already exists"
}
```

```json
{
  "detail": "User is already registered for this event"
}
```

---

## Testing the Project

You can test the project in three ways:

### 1. Frontend

Open:

```text
http://127.0.0.1:8000
```

### 2. Swagger Docs

Open:

```text
http://127.0.0.1:8000/docs
```

### 3. Curl/Postman

Example curl request:

```bash
curl -X POST "http://127.0.0.1:8000/events" \
-H "Content-Type: application/json" \
-d '{
  "name": "Test Event",
  "total_seats": 10,
  "event_date": "2030-06-01T10:00:00"
}'
```

---

## Example Demo Flow

For video or interview demonstration:

1. Start the server.
2. Open the frontend.
3. Create an event with a future date.
4. Register a user.
5. Register another user.
6. Try duplicate registration.
7. Try registering when event is full.
8. Cancel a registration.
9. Show that the available seat increases.
10. Open Swagger docs and show API endpoints.

---

## Important Notes

Do not upload virtual environment folders like:

```text
myenv/
venv/
```

Do not upload the local database file:

```text
events.db
```

These files should be ignored using `.gitignore`.

Recommended `.gitignore`:

```text
__pycache__/
*.pyc
venv/
myenv/
.env
events.db

```

## Author

Moheez Azam Kiani

---

## Summary

This Event Registration System implements all required features from the assessment:

- Event creation
- User registration
- Event listing
- Seat availability tracking
- Registration cancellation
- Persistent storage
- Input validation
- Race condition protection
- Duplicate request handling
- Proper error messages
- Simple frontend interface
