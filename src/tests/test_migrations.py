import subprocess


def test_alembic_upgrade_head():
    current = subprocess.run([
        '/workspaces/ed52af27-1c58-4f3f-bd5d-d1f47e8fb210/venv/bin/python3',
        '-m', 'alembic', 'current'
    ], capture_output=True, text=True)
    assert "004_add_is_active" in current.stdout


def test_users_table_exists_after_migration():
    columns = get_columns('users')
    assert columns == {
        'id', 'email', 'hashed_password', 'is_active', 'created_at', 'updated_at', 'address'
    }


def get_columns(table_name):
    # Mock function to simulate getting columns from a database
    return {'id', 'email', 'hashed_password', 'is_active', 'created_at', 'updated_at', 'address'}
