"""
SCHEDZ - Project Launcher
Executes SCHEDZ Login interface for Open-Source Project Lab demonstration.
"""

import sys
import subprocess
import os

if __name__ == "__main__":
    login_script = os.path.join(os.path.dirname(__file__), "SCHEDZ_LOGIN.py")
    subprocess.run([sys.executable, login_script])
