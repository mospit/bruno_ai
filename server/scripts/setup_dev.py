#!/usr/bin/env python3
"""
Bruno AI Development Setup Script
Set up the development environment for Bruno AI.
"""

import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install project requirements."""
    requirements_file = Path(__file__).parent.parent / "config" / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ Requirements file not found")
        return False
    
    print("📦 Installing requirements...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", str(requirements_file)
        ], check=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def setup_environment():
    """Set up environment configuration."""
    config_dir = Path(__file__).parent.parent / "config"
    env_example = config_dir / ".env.example"
    env_file = config_dir / ".env"
    
    if env_file.exists():
        print("✅ Environment file already exists")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Environment file created from template")
        print("⚠️  Please edit config/.env with your API keys")
        return True
    else:
        print("❌ Environment template not found")
        return False

def create_log_directory():
    """Create logs directory if it doesn't exist."""
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    print("✅ Logs directory ready")

def main():
    """Main setup function."""
    print("🐻 Setting up Bruno AI Development Environment")
    print("=" * 50)
    
    checks = [
        ("Python version", check_python_version),
        ("Requirements", install_requirements), 
        ("Environment", setup_environment),
        ("Log directory", create_log_directory)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ Development environment setup complete!")
        print("\nNext steps:")
        print("1. Edit config/.env with your API keys")
        print("2. Run: python main.py")
        print("3. Run tests: python scripts/run_tests.py")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
