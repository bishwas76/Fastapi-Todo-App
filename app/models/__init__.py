import pkgutil
import importlib
from sqlmodel import SQLModel

# 1. Provide the metadata to be imported by Alembic
metadata = SQLModel.metadata

# 2. Iterate through all files in the current directory (app/models)
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    # 3. Dynamically import each module (e.g., 'user', 'post')
    importlib.import_module(f".{module_name}", package=__name__)