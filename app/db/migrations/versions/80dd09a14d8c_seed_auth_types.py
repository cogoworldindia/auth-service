"""seed auth types

Revision ID: 80dd09a14d8c
Revises: b6adf653272d
Create Date: 2025-11-03 22:10:42.949670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80dd09a14d8c'
down_revision: Union[str, Sequence[str], None] = 'b6adf653272d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

     # Add new column 'status' with default False
    op.add_column('auth_type', sa.Column('status', sa.Boolean(), nullable=False, server_default=sa.false()))

    # Seed auth types
    auth_types = [
        ('email', 'Email verification-based authentication'),
        ('phone', 'Phone OTP-based authentication'),
        ('google', 'Google OAuth provider'),
        ('apple', 'Apple Sign-In provider'),
        ('facebook', 'Facebook OAuth provider'),
        ('firebase', 'Firebase authentication provider'),
    ]

    for type_name, desc in auth_types:
        op.execute(
            sa.text(
                """
                INSERT INTO auth_type (type, description)
                VALUES (:type_name, :desc)
                ON CONFLICT (type) DO NOTHING;
                """
            ).bindparams(type_name=type_name, desc=desc)
        )

     # Update existing records (email, google = true)
    op.execute(
        """
        UPDATE auth_type
        SET status = TRUE
        WHERE type IN ('email', 'phone', 'google');
        """
    )


def downgrade():
    op.execute(
        sa.text(
            """
            DELETE FROM auth_type
            WHERE type IN ('email', 'phone', 'google', 'apple', 'facebook', 'firebase');
            """
        )
    )
    # Drop the 'status' column if rollback
    op.drop_column('auth_type', 'status')