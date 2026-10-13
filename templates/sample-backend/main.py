"""Учебный бэкенд курса: заметки в памяти процесса, без базы данных."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Sample Backend", version="0.1.0")

notes: dict[int, dict] = {}


class NoteIn(BaseModel):
    title: str
    text: str = ""


@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {"message": "Sample Backend"}


@app.get("/health")
async def health_check():
    """Проверка, что сервис жив."""
    return {"status": "healthy"}


@app.post("/notes", status_code=201)
async def create_note(note: NoteIn):
    """Создать заметку."""
    note_id = max(notes, default=0) + 1
    notes[note_id] = {"id": note_id, **note.model_dump()}
    return notes[note_id]


@app.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: int):
    """Удалить заметку по id."""
    if note_id not in notes:
        raise HTTPException(status_code=404, detail="Note not found")
    del notes[note_id]
