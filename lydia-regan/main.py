"""Lydia & Regan: a FastAPI demo for creating and reading journal entries."""

from datetime import datetime, timezone
from threading import Lock

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field


app = FastAPI(
    title="Lydia & Regan",
    description="Journal API demo: create an entry, then retrieve all entries. Data is stored in memory only.",
    version="0.1.0",
)


class EntryCreate(BaseModel):
    """A journal entry submitted by the client as JSON."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100, description="Journal title")
    content: str = Field(min_length=1, max_length=10000, description="Journal content")


class Entry(EntryCreate):
    """A journal entry returned by the server with a generated ID and timestamp."""

    id: int
    created_at: datetime


# In-memory demo storage: resets on restart. Run with a single server process.
entries: list[Entry] = []
# Synchronous route functions can run concurrently, so protect shared storage.
entries_lock = Lock()


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.post(
    "/entries",
    response_model=Entry,
    status_code=status.HTTP_201_CREATED,
    tags=["Journal"],
    summary="Create a journal entry",
)
def create_entry(entry: EntryCreate):
    """Accept a title and content, add an ID and UTC timestamp, then save and return the entry."""
    with entries_lock:
        new_entry = Entry(
            id=len(entries) + 1,
            title=entry.title,
            content=entry.content,
            created_at=datetime.now(timezone.utc),
        )
        entries.append(new_entry)
    return new_entry


@app.get("/entries", response_model=list[Entry], tags=["Journal"], summary="Get all journal entries")
def list_entries():
    """Return a JSON array, or [] if no entries have been created."""
    with entries_lock:
        return entries.copy()


if __name__ == "__main__":
    import uvicorn

    # Right-click and run this file in PyCharm; no working directory setup is needed.
    uvicorn.run(app, host="127.0.0.1", port=8000)
