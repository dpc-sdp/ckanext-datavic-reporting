"""Create report_schedule table\


Revision ID: 390031f5cbb4
Revises:
Create Date: 2022-07-05 18:05:02.477433

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "390031f5cbb4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    if "report_schedule" in tables:
        return

    op.create_table(
        "report_schedule",
        sa.Column("id", sa.UnicodeText, primary_key=True),
        sa.Column(
            "timestamp",
            sa.DateTime,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("user_id", sa.UnicodeText),
        sa.Column("report_type", sa.UnicodeText),
        sa.Column("org_id", sa.UnicodeText),
        sa.Column("sub_org_ids", sa.UnicodeText),
        sa.Column("frequency", sa.UnicodeText),
        sa.Column("user_roles", sa.UnicodeText),
        sa.Column("emails", sa.UnicodeText),
        sa.Column("state", sa.UnicodeText),
        sa.Column("last_completed", sa.DateTime),
    )


def downgrade():
    op.drop_table("report_schedule")
