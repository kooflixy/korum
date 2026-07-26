# Файл, в котором собраны все модели для легкого импорта в migrations/env.py

from features.auth.model import UserORM
from features.posts.model import PostORM

# теперь Base видит все другие модели
from src.db.database import Base
