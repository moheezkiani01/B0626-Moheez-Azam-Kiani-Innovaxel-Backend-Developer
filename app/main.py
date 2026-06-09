from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from app.database import get_connection, initialize_database
from app.models import utc_now_iso
from app.schemas import EventCreate, EventResponse, RegistrationCancel, RegistrationCreate

app = FastAPI(
    title="Event Registration System API",
    description="A simple API for creating events and managing registrations.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.on_event("startup")
def startup():
    initialize_database()

@app.get("/")
def frontend():
    return FileResponse("app/static/index.html")


@app.get("/health")
def health_check():
    return {"message": "Event Registration System API is running"}

@app.post("/events", status_code=201)
def create_event(event: EventCreate):
    now = datetime.now(timezone.utc)

    # If event_date has no timezone, treat it as UTC for simple comparison.
    event_date = event.event_date
    if event_date.tzinfo is None:
        event_date = event_date.replace(tzinfo=timezone.utc)

    if event_date <= now:
        raise HTTPException(status_code=400, detail="Event date must be in the future")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO events (name, total_seats, event_date, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                event.name,
                event.total_seats,
                event_date.isoformat(),
                utc_now_iso(),
            ),
        )
        conn.commit()

        return {
            "id": cursor.lastrowid,
            "name": event.name,
            "total_seats": event.total_seats,
            "event_date": event_date.isoformat(),
        }

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Event name already exists")

    finally:
        conn.close()


@app.get("/events", response_model=list[EventResponse])
def view_events(
    sort_by_date: bool = Query(False),
    upcoming_only: bool = Query(False),
):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        query = """
            SELECT
                e.id,
                e.name,
                e.total_seats,
                e.event_date,
                COUNT(r.id) AS total_registrations,
                e.total_seats - COUNT(r.id) AS available_seats
            FROM events e
            LEFT JOIN registrations r
                ON e.id = r.event_id
                AND r.status = 'active'
        """

        params = []

        if upcoming_only:
            query += " WHERE e.event_date > ?"
            params.append(utc_now_iso())

        query += " GROUP BY e.id"

        if sort_by_date:
            query += " ORDER BY e.event_date ASC"

        cursor.execute(query, params)
        events = cursor.fetchall()

        return [dict(event) for event in events]

    finally:
        conn.close()


@app.post("/registrations", status_code=201)
def register_user(registration: RegistrationCreate):
    """
    Registers a user for an event.

    BEGIN IMMEDIATE prevents race-condition overbooking by allowing only
    one write transaction at a time during the seat availability check and insert.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute(
            "SELECT id, total_seats, event_date FROM events WHERE id = ?",
            (registration.event_id,),
        )
        event = cursor.fetchone()

        if event is None:
            conn.rollback()
            raise HTTPException(status_code=404, detail="Event not found")

        event_date = datetime.fromisoformat(event["event_date"])
        now = datetime.now(timezone.utc)

        if event_date.tzinfo is None:
            event_date = event_date.replace(tzinfo=timezone.utc)

        if event_date <= now:
            conn.rollback()
            raise HTTPException(status_code=400, detail="Cannot register for a past event")

        cursor.execute(
            """
            SELECT COUNT(*) AS active_count
            FROM registrations
            WHERE event_id = ? AND status = 'active'
            """,
            (registration.event_id,),
        )

        active_count = cursor.fetchone()["active_count"]

        if active_count >= event["total_seats"]:
            conn.rollback()
            raise HTTPException(status_code=400, detail="Event is full")

        cursor.execute(
            """
            SELECT id
            FROM registrations
            WHERE event_id = ?
              AND user_name = ?
              AND status = 'active'
            """,
            (registration.event_id, registration.user_name),
        )

        existing_registration = cursor.fetchone()

        if existing_registration is not None:
            conn.rollback()
            raise HTTPException(
                status_code=409,
                detail="User is already registered for this event",
            )

        registered_at = utc_now_iso()

        cursor.execute(
            """
            INSERT INTO registrations (event_id, user_name, status, registered_at)
            VALUES (?, ?, 'active', ?)
            """,
            (
                registration.event_id,
                registration.user_name,
                registered_at,
            ),
        )

        conn.commit()

        return {
            "registration_id": cursor.lastrowid,
            "event_id": registration.event_id,
            "user_name": registration.user_name,
            "status": "active",
            "registered_at": registered_at,
        }

    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate registration request detected",
        )

    finally:
        conn.close()


@app.delete("/registrations")
def cancel_registration(registration: RegistrationCancel):
    """
    Cancels an active registration.

    This does not delete the row. It marks it as cancelled,
    so registration history remains available.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute(
            """
            SELECT id
            FROM registrations
            WHERE event_id = ?
              AND user_name = ?
              AND status = 'active'
            """,
            (registration.event_id, registration.user_name),
        )

        existing_registration = cursor.fetchone()

        if existing_registration is None:
            conn.rollback()
            raise HTTPException(
                status_code=404,
                detail="Active registration not found",
            )

        cursor.execute(
            """
            UPDATE registrations
            SET status = 'cancelled',
                cancelled_at = ?
            WHERE id = ?
            """,
            (utc_now_iso(), existing_registration["id"]),
        )

        conn.commit()

        return {
            "message": "Registration cancelled successfully",
            "event_id": registration.event_id,
            "user_name": registration.user_name,
        }

    finally:
        conn.close()


@app.exception_handler(ValueError)
def value_error_handler(_, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
