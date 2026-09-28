"""Initial Ponup schema."""
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

content_kind = sa.Enum("markdown", "json", "file", name="content_kind")
visibility = sa.Enum("private", "public", name="visibility")
processing_status = sa.Enum("queued", "processing", "ready", "failed", name="processing_status")

def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "spaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_spaces_slug", "spaces", ["slug"], unique=True)
    op.create_table(
        "contents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("space_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("spaces.id", ondelete="CASCADE"), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("kind", content_kind, nullable=False),
        sa.Column("mime_type", sa.String(200), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String(80)), nullable=False, server_default="{}"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("visibility", visibility, nullable=False, server_default="private"),
        sa.Column("processing_status", processing_status, nullable=False, server_default="queued"),
        sa.Column("processing_error", sa.Text()),
        sa.Column("object_key", sa.String(500), nullable=False, unique=True),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("size", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("space_id", "slug", name="uq_content_space_slug"),
    )
    op.create_index("ix_contents_space_id", "contents", ["space_id"])
    op.create_table(
        "content_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("content_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
    )
    op.create_index("ix_content_chunks_content_id", "content_chunks", ["content_id"])
    op.execute("CREATE INDEX ix_content_chunks_embedding_hnsw ON content_chunks USING hnsw (embedding vector_cosine_ops)")

def downgrade() -> None:
    op.drop_table("content_chunks")
    op.drop_table("contents")
    op.drop_table("spaces")
    processing_status.drop(op.get_bind(), checkfirst=True)
    visibility.drop(op.get_bind(), checkfirst=True)
    content_kind.drop(op.get_bind(), checkfirst=True)
