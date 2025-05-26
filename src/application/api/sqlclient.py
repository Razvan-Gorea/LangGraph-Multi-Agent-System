import bcrypt

from sqlmodel import SQLModel, create_engine, Session, select

from application.environment import Environment
from typing import TypeVar, Generator, Any
from contextlib import contextmanager
from sqlalchemy.orm import selectinload

from application.api.models.connector import Connector
from application.api.models.conversation import Conversation
from application.api.models.chat import Chat
from application.api.models.permission import Permission
from application.api.models.user import User
from application.api.models.user_permission import UserPermission

T = TypeVar('T')
class SQLClient:
    def __init__(self, env: Environment, connect_args: dict[str, bool]):
        self.env = env
        self.engine = create_engine(env.SQL_LITE_DB_STRING, connect_args=connect_args)

    def create_db_and_tables(self) -> None:
        """Creates the db and tables. If existing, verifies the structure."""
        SQLModel.metadata.create_all(self.engine)

        tables = [
            Conversation.__table__,
            Chat.__table__,
            User.__table__,
            Permission.__table__,
            UserPermission.__table__,
            Connector.__table__
        ]

        for table in tables:
            table.create(self.engine, checkfirst=True)

    def drop_all_tables(self) -> None:
        """Drops all tables in the database. Use with caution!"""
        SQLModel.metadata.drop_all(self.engine)

    @contextmanager
    def get_session(self)-> Generator[Session, Any, None]:
        """Yield a session of the objects engine."""
        session = Session(self.engine)
        yield session
    
    def hash_password(self, password: str) -> str:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')

    def compare_hash(self, plaintext: str, hashed: str) -> bool:
        if bcrypt.checkpw(plaintext.encode('utf-8'), hashed.encode('utf-8')):
            return True
        return False

    def add_object(self, to_save: T) -> T:
        """Add an object to the db. Takes generics."""

        if hasattr(to_save, "password") and to_save.password:
            to_save.password = self.hash_password(to_save.password)

        with self.get_session() as session:
            session.add(to_save)
            session.commit()
            session.refresh(to_save)
            session.close()
        return to_save

    def bulk_add_object(self, to_insert: list[T]) -> None:
        """Take the list of objects, insert them """
        
        if hasattr(to_insert[0], "password"):
           for user in to_insert:
               user.password = self.hash_password(user.password)

        with self.get_session() as session:
            session.add_all(to_insert)
            session.commit()
            for obj in to_insert:
                session.refresh(obj)
            session.close()

    def replace_object(self, original: T, replacement: T) -> T:
        """Replace an existing object in the db. Needs the original object and the new object."""
        original.sqlmodel_update(replacement)
        with self.get_session() as session:
            session.add(original)
            session.commit()
            session.refresh(original)
            session.close()
        return original

    def delete_object(self, to_delete: T) -> None:
        """Delete a record. Takes the object to delete. """
        with self.get_session() as session:
            session.delete(to_delete)
            session.commit()
            session.close()
 
    def get_by_id(self, table: T, primary_key: int, eager_relationships: list = None) -> Any:
        """Fetch a record on its primary key with optional eager loading of relationships.
           Uses an internal session.
        """
        with self.get_session() as session:
            statement = select(table).where(getattr(table, "id") == primary_key)

            if eager_relationships:
                for relationship in eager_relationships:
                    statement = statement.options(selectinload(relationship))

            obj = session.exec(statement).first()
            session.close()
            return obj
    
    def get_by_email(self, table: T, email: str) -> Any:
        """Fetch a record by email. Returns None if not found."""
        with self.get_session() as session:
            obj = session.query(table).filter_by(email=email).first()
            session.close()
            return obj

    def get_latest_conversation(self, user_id: int) -> Any:
        conversations = self.get_by_column(Conversation, "user_id", user_id)
        if len(conversations) < 1:
            return None
            
        return max(conversations, key=lambda obj: getattr(obj, "last_modified_date"))

    def get_by_column(self, table: T, column_name: str, value: Any) -> Any:
        column = getattr(table, column_name, None)
        if column is None:
            return None

        with self.get_session() as session:
            results = session.query(table).filter(column == value).all()
            session.close()
        return results
    
    def get_all_records(self, table: T) -> list[Any]:
        with self.get_session() as session:
            results = session.query(table).all()
            session.close()
        return results
