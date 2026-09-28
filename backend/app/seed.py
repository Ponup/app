from sqlalchemy import select

from app.core.db import SessionLocal
from app.models import Space
from app.schemas import ContentCreate, SpaceCreate
from app.services.content import create_content, create_space
from app.worker import enqueue

with SessionLocal() as db:
    space = db.scalar(select(Space).where(Space.slug == "welcome"))
    if not space:
        space = create_space(db, SpaceCreate(name="Welcome", description="Your first Ponup Space"))
        content = create_content(
            db,
            space,
            ContentCreate(
                title="Getting started",
                kind="markdown",
                tags=["welcome", "guide"],
                body="# Welcome to Ponup\n\nCreate, connect, and retrieve your context.",
            ),
        )
        enqueue(content.id)
        print(f"Created demo space {space.slug}")
    else:
        print("Demo space already exists")
