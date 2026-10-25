import os
import sys

# Ensure root directory is on Python path for Vercel Serverless Function execution
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.main import app

# Expose app for Vercel
__all__ = ["app"]
