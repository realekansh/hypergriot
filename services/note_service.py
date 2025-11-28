from typing import Optional, List
from db.session import SessionLocal
from db import models

def create_or_update_note(chat_id: int, name: str, text: str, creator_id: Optional[int] = None):
    with SessionLocal() as db:
        note = db.query(models.Note).filter(models.Note.chat_id == chat_id, models.Note.name == name).first()
        if note:
            note.text = text
            note.created_by = creator_id
        else:
            note = models.Note(chat_id=chat_id, name=name, text=text, created_by=creator_id)
            db.add(note)
        db.commit()
        return note

def get_note(chat_id: int, name: str) -> Optional[models.Note]:
    with SessionLocal() as db:
        return db.query(models.Note).filter(models.Note.chat_id == chat_id, models.Note.name == name).first()

def list_notes(chat_id: int) -> List[models.Note]:
    with SessionLocal() as db:
        return db.query(models.Note).filter(models.Note.chat_id == chat_id).order_by(models.Note.created_at.desc()).all()

def delete_note(chat_id: int, name: str) -> bool:
    with SessionLocal() as db:
        note = db.query(models.Note).filter(models.Note.chat_id == chat_id, models.Note.name == name).first()
        if not note:
            return False
        db.delete(note)
        db.commit()
        return True
