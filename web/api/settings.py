from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from web.auth import require_token
from db.session import SessionLocal
from db import models

router = APIRouter(prefix="/api/settings", dependencies=[Depends(require_token)])

@router.get("/get/{chat_id}")
def get_settings(chat_id: int):
    with SessionLocal() as db:
        cs = db.query(models.ChatSettings).filter(models.ChatSettings.chat_id == chat_id).first()
        if not cs:
            raise HTTPException(status_code=404, detail="Chat not found")
        return cs.settings or {}

@router.post("/set/{chat_id}")
def set_settings(chat_id: int, payload: dict):
    with SessionLocal() as db:
        cs = db.query(models.ChatSettings).filter(models.ChatSettings.chat_id == chat_id).first()
        if not cs:
            cs = models.ChatSettings(chat_id=chat_id, settings=payload)
            db.add(cs)
        else:
            cs.settings = payload
        db.commit()
        return {"ok": True}
