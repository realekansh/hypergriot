Jobs / Workers

This folder contains background workers for scheduled tasks:
 - unban_worker.py: scans DB for expired bans/mutes and unbans/unmutes users.
 - purge_worker.py: placeholder for purge job processing.
 - scheduler.py: runs the workers with a Pyrogram client.

Run workers with:
  python -m jobs.scheduler

In production, run the scheduler in a separate process or container. Use supervisord, systemd, or a container orchestrator for reliability.
