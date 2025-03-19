from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
import re


@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models.
    """
    id: Any
    __name__: str
    
    # Generate tablename automatically from class name
    @declared_attr
    def __tablename__(cls) -> str:
        # Convert CamelCase to snake_case
        name = re.sub('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))', r'_\1', cls.__name__).lower()
        return name
