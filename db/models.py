# db/models.py
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, JSON, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression
import enum
import uuid
from .session import Base

class ActionType(enum.Enum):
    BAN = "ban"
    UNBAN = "unban"
    MUTE = "mute"
    UNMUTE = "unmute"
    KICK = "kick"
    PURGE = "purge"
    FILTER = "filter"
    AUTO = "auto"

def gen_uuid():
    return str(uuid.uuid4())

class ChatSettings(Base):
    __tablename__ = "chat_settings"
    chat_id = Column(BigInteger, primary_key=True, index=True)
    settings = Column(JSON, nullable=False, server_default="{}")  # JSON blob for flexible settings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Note(Base):
    __tablename__ = "notes"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    chat_id = Column(BigInteger, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    text = Column(Text, nullable=False)
    created_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    pinned = Column(Boolean, default=False)

    __table_args__ = (
        # enforces unique note names per chat
        {},
    )

class Filter(Base):
    __tablename__ = "filters"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    chat_id = Column(BigInteger, index=True, nullable=False)
    type = Column(String(32), nullable=False)  # word|regex|link|media|sticker|file
    pattern = Column(Text, nullable=False)
    flags = Column(JSON, nullable=True)
    action = Column(String(64), nullable=False, default="delete")  # delete|warn|mute:10m|...
    silent = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    severity = Column(Integer, default=1)
    hit_count = Column(Integer, default=0)
    hit_sample = Column(JSON, nullable=True)
    created_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ModLog(Base):
    __tablename__ = "mod_logs"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    chat_id = Column(BigInteger, index=True)
    moderator_id = Column(BigInteger, nullable=True)  # null => bot/auto
    action = Column(String(32), nullable=False)
    target_user = Column(BigInteger, nullable=True)
    reason = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Ban(Base):
    __tablename__ = "bans"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    chat_id = Column(BigInteger, index=True)
    user_id = Column(BigInteger, index=True)
    type = Column(String(32), nullable=False)  # PERM | TEMP | SILENT | DELETE_AND_BAN
    reason = Column(Text, nullable=True)
    moderator_id = Column(BigInteger, nullable=True)
    message_id_deleted = Column(BigInteger, nullable=True)
    start_ts = Column(DateTime(timezone=True), server_default=func.now())
    end_ts = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True)

class Mute(Base):
    __tablename__ = "mutes"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    chat_id = Column(BigInteger, index=True)
    user_id = Column(BigInteger, index=True)
    type = Column(String(32), nullable=False)  # PERM | TEMP | SILENT | DELETE_AND_MUTE
    mute_mode = Column(String(32), nullable=True)  # FULL | MEDIA_ONLY
    reason = Column(Text, nullable=True)
    moderator_id = Column(BigInteger, nullable=True)
    message_id_deleted = Column(BigInteger, nullable=True)
    start_ts = Column(DateTime(timezone=True), server_default=func.now())
    end_ts = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True)
