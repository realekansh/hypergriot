from typing import List, Dict, Any
from db.session import SessionLocal
from db import models
import re

def load_enabled_filters(chat_id: int) -> List[models.Filter]:
    with SessionLocal() as db:
        return db.query(models.Filter).filter(models.Filter.chat_id == chat_id, models.Filter.enabled == True).all()

def test_message_against_filters(chat_id: int, text: str) -> List[Dict[str, Any]]:
    """
    Returns list of matched filters with info: [{'id':..., 'action':..., 'filter':...}, ...]
    """
    matches = []
    filters = load_enabled_filters(chat_id)
    for f in filters:
        try:
            if f.type == "word":
                pattern = f.pattern
                # whole-word match by default
                if re.search(rf'\\b{re.escape(pattern)}\\b', text, flags=re.IGNORECASE):
                    matches.append({"id": f.id, "action": f.action, "filter": f})
            elif f.type == "regex":
                flags = 0
                # flags stored in f.flags JSON if needed
                if re.search(f.pattern, text):
                    matches.append({"id": f.id, "action": f.action, "filter": f})
            elif f.type == "link":
                # simple URL substring check
                if f.pattern.lower() in text.lower():
                    matches.append({"id": f.id, "action": f.action, "filter": f})
            else:
                # other types: implement later
                pass
        except Exception:
            # ignore filter eval errors (but in production log them)
            pass
    return matches

def record_filter_hit(filter_id: str, chat_id: int, message_id: int, user_id: int, snippet: str = ""):
    with SessionLocal() as db:
        f = db.query(models.Filter).filter(models.Filter.id == filter_id).first()
        if not f:
            return
        f.hit_count = (f.hit_count or 0) + 1
        # append to sample (simple list)
        sample = f.hit_sample or []
        sample = sample if isinstance(sample, list) else []
        sample.insert(0, {"message_id": message_id, "user_id": user_id, "snippet": snippet})
        f.hit_sample = sample[:10]
        db.add(f)
        db.commit()
