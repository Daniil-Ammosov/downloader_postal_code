"""Creates addr_objects and house_objects tables

Revision ID: ed65b559ace1
Revises:
Create Date: 2019-01-25 16:08:45.292964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed65b559ace1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'addr_objects',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('region_code', sa.String(length=2), nullable=False, index=True),
        sa.Column('area_code', sa.String(length=3), nullable=False, index=True),
        sa.Column('city_code', sa.String(length=3), nullable=False, index=True),
        sa.Column('place_code', sa.String(length=3), nullable=False, index=True),
        sa.Column('plane_code', sa.String(length=4), nullable=False, index=True),
        sa.Column('street_code', sa.String(length=4), nullable=False, index=True),
        sa.Column('short_name', sa.String(length=10), nullable=False, index=True),
        sa.Column('off_name', sa.String(length=120), nullable=False, index=True),
        sa.Column('okato', sa.String(length=11),    nullable=False, index=True),
        sa.Column('oktmo', sa.String(length=11),    nullable=False, index=True),
        sa.Column('postal_code', sa.String(length=6), nullable=False, index=True),
        sa.Column('ao_level', sa.Integer(), nullable=False, index=True),
        sa.Column('code', sa.String(length=17), nullable=False, index=True),
        sa.Column('ao_guid', sa.String(length=36), nullable=False, index=True),
        sa.Column('parent_guid', sa.String(length=36), nullable=False, index=True),
        mysql_engine=u"MyISAM"
    )

    op.create_table(
        'house_objects',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('ao_guid',        sa.String(length=36),       nullable=False, index=True),
        sa.Column('house_guid',     sa.String(length=36),       nullable=False, index=True),
        sa.Column('house_num',      sa.String(length=20),       nullable=False, index=True),
        sa.Column('build_num',      sa.String(length=50),       nullable=False, index=True),
        sa.Column('struc_num',      sa.String(length=50),       nullable=False, index=True),
        sa.Column('postal_code',    sa.String(length=6),        nullable=False, index=True),
        sa.Column('okato',          sa.String(length=11),       nullable=False, index=True),
        sa.Column('oktmo',          sa.String(length=11),       nullable=False, index=True),
        sa.Column('joined_num',     sa.String(length=120), nullable=False, index=True),
        mysql_engine=u"MyISAM"
    )

    release = op.create_table(
        "release",
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('version', sa.Integer, nullable=False, default=0)
    )
    op.bulk_insert(release, [{"id": 1}])


def downgrade():
    op.drop_table("house_objects")
    op.drop_table("release")
    op.drop_table("addr_objects")
