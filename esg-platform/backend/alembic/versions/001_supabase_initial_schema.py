"""supabase initial schema and rls policies

Revision ID: 001_supabase_initial_schema
Revises: 
Create Date: 2026-09-17 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_supabase_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Enable pgvector extension (Supabase Postgres)
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == 'postgresql':
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('subscription_tier', sa.String(length=50), nullable=False, server_default='starter'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_slug'), 'organizations', ['slug'], unique=True)

    # 3. Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='EMPLOYEE'),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='SET NULL'),
    )
    op.create_index(op.f('ix_user_profiles_email'), 'user_profiles', ['email'], unique=True)
    op.create_index(op.f('ix_user_profiles_organization_id'), 'user_profiles', ['organization_id'], unique=False)

    # 4. Create facilities table
    op.create_table(
        'facilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('state_province', sa.String(length=100), nullable=True),
        sa.Column('facility_type', sa.String(length=100), nullable=False, server_default='office'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_facilities_id'), 'facilities', ['id'], unique=False)
    op.create_index(op.f('ix_facilities_organization_id'), 'facilities', ['organization_id'], unique=False)

    # 5. Enable RLS Policies for Supabase Postgres
    if dialect == 'postgresql':
        op.execute("ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;")
        op.execute("ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;")
        op.execute("ALTER TABLE facilities ENABLE ROW LEVEL SECURITY;")

        # Enable service_role full access policy
        op.execute("""
            CREATE POLICY service_role_organizations ON organizations
            FOR ALL USING (auth.role() = 'service_role');
        """)
        op.execute("""
            CREATE POLICY service_role_user_profiles ON user_profiles
            FOR ALL USING (auth.role() = 'service_role');
        """)
        op.execute("""
            CREATE POLICY service_role_facilities ON facilities
            FOR ALL USING (auth.role() = 'service_role');
        """)


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == 'postgresql':
        op.execute("DROP POLICY IF EXISTS service_role_facilities ON facilities;")
        op.execute("DROP POLICY IF EXISTS service_role_user_profiles ON user_profiles;")
        op.execute("DROP POLICY IF EXISTS service_role_organizations ON organizations;")

    op.drop_index(op.f('ix_facilities_organization_id'), table_name='facilities')
    op.drop_index(op.f('ix_facilities_id'), table_name='facilities')
    op.drop_table('facilities')

    op.drop_index(op.f('ix_user_profiles_organization_id'), table_name='user_profiles')
    op.drop_index(op.f('ix_user_profiles_email'), table_name='user_profiles')
    op.drop_table('user_profiles')

    op.drop_index(op.f('ix_organizations_slug'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')
