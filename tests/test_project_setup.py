import os
import subprocess
import pytest

@pytest.mark.order(1)
def test_project_scaffolding():
    # Run the command to scaffold the project
    result = subprocess.run(['nest', 'new', 'my-backend', '--skip-install'], capture_output=True, text=True)
    assert result.returncode == 0, f"Scaffolding failed: {result.stderr}"
    
    # Verify the folder structure
    expected_structure = [
        'my-backend/package.json',
        'my-backend/tsconfig.json',
        'my-backend/nest-cli.json',
        'my-backend/src/main.ts',
        'my-backend/src/app.module.ts',
        'my-backend/src/config/',
        'my-backend/src/common/filters/',
        'my-backend/src/common/guards/',
        'my-backend/src/common/interceptors/',
        'my-backend/src/common/pipes/',
        'my-backend/src/common/dto/',
        'my-backend/src/modules/',
        'my-backend/database/migrations/',
        'my-backend/database/seeds/',
        'my-backend/test/'
    ]
    for path in expected_structure:
        assert os.path.exists(path), f"Expected path {path} does not exist"
