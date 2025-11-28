#!/usr/bin/env python3
"""
Dump modlogs to JSON file:
  python extras/export_modlogs.py [--chat CHID] [--out file.json]

If DATABASE_URL is in .env it will be used automatically.
"""
import os, json, sys, argparse
from dotenv import load_dotenv
load_dotenv()
from db.session import SessionLocal
from db import models

def dump(chat_id=None, out_path=None):
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
    if not out_path:
        out_path = f"extras/modlogs_export_{chat_id or 'all'}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(out)} rows to {out_path}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chat", type=int, help="chat_id to filter")
    p.add_argument("--out", type=str, help="output file path")
    args = p.parse_args()
    dump(chat_id=args.chat, out_path=args.out)

if __name__ == "__main__":
    main()
