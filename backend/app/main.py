import html
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import IntegrityError
from strawberry.fastapi import GraphQLRouter

from app.api.routes import public_content, public_router, router
from app.core.db import SessionLocal
from app.graphql.schema import schema
from app.mcp.server import mcp
from app.models import ContentKind
from app.services import content as content_service

mcp_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Ponup", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(public_router)
app.include_router(GraphQLRouter(schema), prefix="/graphql")


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_: Request, exc: IntegrityError):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=409, content={"detail": "A conflicting resource already exists"})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/p/{space_slug}/{content_slug}", response_class=HTMLResponse)
def public_page(space_slug: str, content_slug: str):
    with SessionLocal() as db:
        value = public_content(db, space_slug, content_slug)
        raw_url = f"/public/v1/spaces/{space_slug}/contents/{content_slug}/raw"
        if value.mime_type.startswith("image/"):
            rendered = f'<img src="{html.escape(raw_url)}" alt="{html.escape(value.title)}">'
        elif value.kind == ContentKind.file:
            rendered = f'<p><a href="{html.escape(raw_url)}">Download this content</a></p>'
        else:
            body = content_service.body_for(value)
            body_text = body if isinstance(body, str) else __import__("json").dumps(body, indent=2)
            rendered = f"<pre>{html.escape(body_text)}</pre>"
        tags = " ".join(f"<span>#{html.escape(tag)}</span>" for tag in value.tags)
        return f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{html.escape(value.title)} · Ponup</title><style>
body{{font:16px/1.6 system-ui;max-width:800px;margin:4rem auto;padding:0 1rem;color:#24231f;background:#faf9f5}}
pre{{white-space:pre-wrap;background:white;padding:1.5rem;border:1px solid #ddd;border-radius:12px}}img{{max-width:100%}}
span{{margin-right:.5rem;color:#6b685f}}a{{color:#195f50}}</style></head><body>
<main><p>Published with Ponup</p><h1>{html.escape(value.title)}</h1><p>{html.escape(value.description)}</p>
<p>{tags}</p>{rendered}</main></body></html>"""


# Keep the catch-all MCP ASGI mount last so application routes retain priority.
app.mount("/", mcp_app)
