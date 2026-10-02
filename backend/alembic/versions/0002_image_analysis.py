"""Store image analysis and extracted image text."""

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("contents", sa.Column("image_analysis", sa.JSON(), nullable=True))
    op.add_column("contents", sa.Column("extracted_text", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("contents", "extracted_text")
    op.drop_column("contents", "image_analysis")
