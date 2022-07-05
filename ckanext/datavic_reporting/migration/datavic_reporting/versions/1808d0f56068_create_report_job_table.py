"""Create report_job table

Revision ID: 1808d0f56068
Revises: 390031f5cbb4
Create Date: 2022-07-05 18:05:16.614061

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '1808d0f56068'
down_revision = '390031f5cbb4'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    if "report_job" in tables:
        return

    op.create_table(
        "report_job",
        sa.Column("id", sa.UnicodeText, primary_key=True),
        sa.Column("report_schedule_id", sa.UnicodeText),
        sa.Column("timestamp", sa.DateTime, server_default=sa.func.current_timestamp(),),
        sa.Column("filename", sa.UnicodeText),
        sa.Column("frequency", sa.UnicodeText),
        sa.Column("user_roles", sa.UnicodeText),
        sa.Column("emails", sa.UnicodeText),
        sa.Column("status", sa.UnicodeText),
    )



def downgrade():
    op.drop_table(    "report_job")
