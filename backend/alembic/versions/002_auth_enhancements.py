"""Auth enhancements

Revision ID: 002
Revises: 001_initial_migration
Create Date: 2025-03-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_role and user_status enum types
    op.execute("CREATE TYPE user_role AS ENUM ('user', 'admin', 'super_admin')")
    
    # Add new columns to the user table
    op.add_column('user', sa.Column('role', sa.Enum('user', 'admin', 'super_admin', name='user_role'), nullable=False, server_default='user'))
    op.add_column('user', sa.Column('oauth_provider', sa.String(), nullable=True))
    op.add_column('user', sa.Column('oauth_id', sa.String(), nullable=True))
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user', sa.Column('email_verified_at', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('user', sa.Column('last_failed_login', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('locked_until', sa.DateTime(), nullable=True))
    
    # Make hashed_password nullable for OAuth users
    op.alter_column('user', 'hashed_password', nullable=True)
    
    # Create the permission table
    op.create_table(
        'permission',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('resource', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create index on permission resource and action
    op.create_index('ix_permission_resource_action', 'permission', ['resource', 'action'], unique=True)
    
    # Create user_permissions association table
    op.create_table(
        'user_permissions',
        sa.Column('user_id', sa.String(), sa.ForeignKey('user.id', ondelete='CASCADE')),
        sa.Column('permission_id', sa.String(), sa.ForeignKey('permission.id', ondelete='CASCADE')),
        sa.PrimaryKeyConstraint('user_id', 'permission_id')
    )
    
    # Create index on oauth_provider and oauth_id
    op.create_index('ix_user_oauth_provider_id', 'user', ['oauth_provider', 'oauth_id'], unique=True)
    
    # Create initial permissions
    op.execute(
        """
        INSERT INTO permission (id, name, description, resource, action)
        VALUES 
        ('1', 'read_users', 'Can read user information', 'users', 'read'),
        ('2', 'write_users', 'Can create and update users', 'users', 'write'),
        ('3', 'delete_users', 'Can delete users', 'users', 'delete'),
        ('4', 'read_interviews', 'Can view interview information', 'interviews', 'read'),
        ('5', 'manage_interviews', 'Can manage interview data', 'interviews', 'manage'),
        ('6', 'read_questions', 'Can view question information', 'questions', 'read'),
        ('7', 'manage_questions', 'Can manage question data', 'questions', 'manage'),
        ('8', 'read_statistics', 'Can view statistics', 'statistics', 'read'),
        ('9', 'manage_system', 'Can manage system settings', 'system', 'manage'),
        ('10', 'manage_roles', 'Can manage user roles', 'roles', 'manage')
        """
    )


def downgrade():
    # Drop user_permissions association table
    op.drop_table('user_permissions')
    
    # Drop permission table
    op.drop_table('permission')
    
    # Drop new columns from user table
    op.drop_column('user', 'role')
    op.drop_column('user', 'oauth_provider')
    op.drop_column('user', 'oauth_id')
    op.drop_column('user', 'email_verified')
    op.drop_column('user', 'email_verified_at')
    op.drop_column('user', 'failed_login_attempts')
    op.drop_column('user', 'last_failed_login')
    op.drop_column('user', 'locked_until')
    
    # Make hashed_password not nullable again
    op.alter_column('user', 'hashed_password', nullable=False)
    
    # Drop user_role enum type
    op.execute("DROP TYPE user_role")
