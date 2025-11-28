from fastapi import APIRouter, Depends, Query, Response
from typing import List, Optional
from web.auth import require_token
from db.session import SessionLocal
from db import models
import json

router = APIRouter(prefix="/api/modlogs", dependencies=[Depends(require_token)])

@router.get("/list")
def list_modlogs(chat_id: Optional[int] = Query(None), limit: int = 100):
    """
    Return last `limit` modlog entries, optionally filtered by chat_id.
    """
    with SessionLocal() as db:
        q = db.query(models.ModLog).order_by(models.ModLog.created_at.desc()).limit(limit)
        if chat_id:
            q = q.filter(models.ModLog.chat_id == chat_id)
        rows = q.all()
        out = []
        for r in rows:
            out.append({
                "id": str(r.id),
                "chat_id": r.chat_id,
                "moderator_id": r.moderator_id,
                "action": r.action,
                "target_user": r.target_user,
                "reason": r.reason,
                "metadata": getattr(r, "metadata_json", {}) or {},
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })
        return out

@router.get("/export")
def export_modlogs(chat_id: Optional[int] = Query(None)):
    """
    Export modlogs as JSON (all entries for chat or all).
    """
    with SessionLocal() as db:
        q = db.query(models.ModLog).order_by(models.ModLog.created_at.desc())
        if chat_id:
            q = q.filter(models.ModLog.chat_id == chat_id)
        rows = q.all()
        out = []
        for r in rows:
            out.append({
                "id": str(r.id),
                "chat_id": r.chat_id,
                "moderator_id": r.moderator_id,
                "action": r.action,
                "target_user": r.target_user,
                "reason": r.reason,
                "metadata": getattr(r, "metadata_json", {}) or {},
                "created_at": r.created_at.isoformat() if r.created_at else None,
            })
        blob = json.dumps(out, indent=2)
        return Response(content=blob, media_type="application/json")
