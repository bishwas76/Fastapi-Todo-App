from IPython import start_ipython
from traitlets.config import Config

STARTUP_CODE = """
import os
import json
import asyncio
from datetime import datetime

# Database imports
from sqlmodel import select, or_, and_, col
from sqlalchemy.orm import selectinload, joinedload
from app.db.database import async_session_maker, engine

# App and Models
from app.app import app
import app.models

print('\\n' + '='*50)
print('---------FastAPI Interactive Shell---------')
print('='*50)
print('Pre-loaded objects available:')
print('  - async_session_maker : Create database sessions')
print('  - engine              : The AsyncEngine')
print('  - select, or_, and_   : SQLModel/SQLAlchemy helpers')
print('  - selectinload        : For eager loading relationships')
print('  - app                 : Your FastAPI application')
print('  - app.models          : All your database models')
print('\\nTip: IPython natively supports top-level `await`!')
print('='*50 + '\\n')
"""

c = Config()
c.InteractiveShellApp.exec_lines = [STARTUP_CODE]
c.InteractiveShell.colors = "Linux"

if __name__ == "__main__":
    start_ipython(argv=[], config=c)
