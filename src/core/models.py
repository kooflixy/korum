# Файл, в котором собраны все модели для легкого импорта в migrations/env.py

# теперь Base видит все другие модели
from src.db.database import Base
from src.features.posts.model import PostORM
from src.features.users.model import UserORM
