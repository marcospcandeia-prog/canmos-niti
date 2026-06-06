"""
Project Validation Script
Checks for common issues in the CANMOS-NITI project
"""

import os
import sys
from pathlib import Path


def check_init_files():
    """Check if all Python packages have __init__.py"""
    print("Checking __init__.py files...")
    
    backend_path = Path(__file__).parent.parent
    missing = []
    
    for dirpath, dirnames, filenames in os.walk(backend_path / "app"):
        # Skip __pycache__ and .git
        dirnames[:] = [d for d in dirnames if d not in ['__pycache__', '.git', '.pytest_cache']]
        
        # Check if directory has Python files
        has_python = any(f.endswith('.py') for f in filenames)
        has_init = '__init__.py' in filenames
        
        if has_python and not has_init:
            missing.append(dirpath)
    
    if missing:
        print(f"ERROR Missing __init__.py in {len(missing)} directories:")
        for m in missing:
            print(f"   - {m}")
        return False
    else:
        print("OK - All packages have __init__.py")
        return True


def check_imports():
    """Check for common import issues"""
    print("\nChecking imports...")
    
    issues = []
    backend_path = Path(__file__).parent.parent
    
    # Check for wrong imports
    wrong_imports = [
        "from app.shared.models.declaration import",  # Should be from tax
    ]
    
    for py_file in backend_path.rglob("*.py"):
        if '__pycache__' in str(py_file) or 'scripts' in str(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            for wrong in wrong_imports:
                if wrong in content:
                    issues.append(f"{py_file}: {wrong}")
        except:
            pass
    
    if issues:
        print(f"ERROR Found {len(issues)} import issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("OK No import issues found")
        return True


def check_env_example():
    """Check if .env.example exists"""
    print("\nChecking .env.example...")
    
    root = Path(__file__).parent.parent.parent
    env_example = root / ".env.example"
    
    if not env_example.exists():
        print("ERROR .env.example not found")
        return False
    
    # Check required vars
    content = env_example.read_text()
    required = [
        "DATABASE_URL",
        "SUPABASE_URL",
        "JWT_SECRET",
        "MINIO_ENDPOINT",
    ]
    
    missing = [r for r in required if r not in content]
    
    if missing:
        print(f"ERROR Missing required vars in .env.example: {missing}")
        return False
    
    print("OK .env.example is valid")
    return True


def check_requirements():
    """Check if requirements.txt exists and has basic packages"""
    print("\nChecking requirements.txt...")
    
    backend_path = Path(__file__).parent.parent
    req_file = backend_path / "requirements.txt"
    
    if not req_file.exists():
        print("ERROR requirements.txt not found")
        return False
    
    content = req_file.read_text()
    required_packages = [
        "fastapi",
        "sqlalchemy",
        "alembic",
        "pydantic",
        "minio",
    ]
    
    missing = [p for p in required_packages if p not in content.lower()]
    
    if missing:
        print(f"ERROR Missing packages in requirements.txt: {missing}")
        return False
    
    print("OK requirements.txt is valid")
    return True


def check_alembic():
    """Check if alembic is configured"""
    print("\nChecking Alembic configuration...")
    
    backend_path = Path(__file__).parent.parent
    alembic_ini = backend_path / "alembic.ini"
    alembic_env = backend_path / "alembic" / "env.py"
    
    if not alembic_ini.exists():
        print("ERROR alembic.ini not found")
        return False
    
    if not alembic_env.exists():
        print("ERROR alembic/env.py not found")
        return False
    
    print("OK Alembic is configured")
    return True


def main():
    """Run all validation checks"""
    print("=" * 60)
    print("CANMOS-NITI Project Validation")
    print("=" * 60)
    
    checks = [
        check_init_files,
        check_imports,
        check_env_example,
        check_requirements,
        check_alembic,
    ]
    
    results = [check() for check in checks]
    
    print("\n" + "=" * 60)
    if all(results):
        print("OK ALL CHECKS PASSED")
        print("=" * 60)
        return 0
    else:
        failed = len([r for r in results if not r])
        print(f"ERROR {failed} CHECK(S) FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
