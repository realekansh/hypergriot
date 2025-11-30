# HyperGriot Architecture Overview

HyperGriot is structured into isolated modules designed for stability, readability, and long-term maintainability.

## 1. Major Components
- **bot/** – Pyrogram handlers, middleware, command registry, callback routers.  
- **services/** – Business logic: moderation actions, filters, captcha, flood control, antiflood, antiraid, cache, redis, etc.  
- **db/** – SQLAlchemy ORM models, engine setup, migrations.  
- **jobs/** – Background tasks: queues, cron jobs, cleanup workers, async tasks.  
- **web/** – FastAPI-based dashboard backend providing APIs for logs, statistics, settings, tokens.  
- **extras/** – Pure helper modules: time parsers, markdown safe mode, text utilities, etc.  
- **tests/** – Unit tests verifying stability and reliability of core logic.  

## 2. Core Design Ideas
- Each module only does one job and exposes clean interfaces.
- No circular imports — services never import handlers.
- All database operations go through service layers.
- All handlers depend only on:
  - services  
  - utils  
  - db models  
- Strong typing & minimal ambiguity.
- Command registry powers dynamic `/help` generation.

## 3. Flow Example (Moderation Action)
1. User triggers command `/ban`.  
2. Handler parses args → calls service.  
3. Service validates permissions + rules.  
4. Service executes action (kick/ban/mute) via Pyrogram.  
5. Service logs event via db.  
6. Dashboard can read logs through API.  

