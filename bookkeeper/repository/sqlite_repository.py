""" This module contains the SqliteRepository class, which implements
    the AbstractRepository class for SQLite databases.

Classes:

    SqliteRepository: Implements the abstract methods of the AbstractRepository class for
    SQLite databases.

Functions:

    None """

import os
import sqlite3
from typing import Any, Dict, List, Optional, Type, cast

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SqliteRepository(AbstractRepository[T]):
    """ This class implements the AbstractRepository class for SQLite databases.
    It provides methods to add, get, get_all, update and delete records from the
    SQLite database for two models: Category and Expense.

Attributes:

    conn (sqlite3.Connection): The SQLite database connection.
    cursor (sqlite3.Cursor): The SQLite database cursor.
    model_class (Type[T]): The type of model (Category or Expense) that
                           this repository is working with.

Methods:

    init(self, db_path: str, model_class: Type[T]): Initializes the SQLite database
        connection and creates the table for the corresponding model if it doesn’t
        exist already.
    add(self, obj: T) -> int: Adds a new record to the database for the given model.
    get(self, pk: int) -> Optional[T]: Retrieves a record from the database with the
        given primary key for the given model.
    get_all(self, where: Optional[Dict[str, Any]] = None) -> List[T]: Retrieves all
        records from the database for the given model. If a where dictionary is given,
        it is used to filter the results.
    delete(self, pk: int) -> None: Deletes a record from the database with the given
        primary key for the given model.
    update(self, obj: T) -> None: Updates a record in the database with the given object
        for the given model.
    get_category_by_name(self, name: str) -> Optional[Category]: Retrieves a category
        record from the database with the given name.

Raises:

    ValueError: If the database file doesn’t exist or if there is an error
        opening the database.
    TypeError: If an unsupported object type is used.

"""

    def __init__(self, db_path: str, model_class: Type[T]):
        if not os.path.isfile(db_path):
            raise ValueError(f"Database file {db_path} does not exist")

        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as error:
            raise ValueError(f"Failed to open database {db_path}: {error}") from error
        self.model_class = model_class
        if self.model_class == Category:
            # create table for categories
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    pk INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parent INTEGER REFERENCES categories(pk)
                )
            """)
        elif self.model_class == Expense:
            # create table for expenses
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    pk INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount INTEGER NOT NULL,
                    category INTEGER NOT NULL,
                    expense_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    added_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    comment TEXT,
                    FOREIGN KEY (category) REFERENCES categories (pk) ON DELETE CASCADE
                )
            """)
        else:
            raise ValueError(f"Unsupported model class: {self.model_class.__name__}")

        self.conn.commit()

    def add(self, obj: T) -> int:
        if isinstance(obj, Category):
            # check if the category already exists in the table
            existing_category = self.get_category_by_name(obj.name)
            if existing_category:
                return existing_category.pk

            # if not, insert the new category
            self.cursor.execute("INSERT INTO categories (name, parent) VALUES (?, ?)",
                                (obj.name, obj.parent))
            self.conn.commit()
            obj.pk = cast(int, self.cursor.lastrowid)
            return obj.pk

        if isinstance(obj, Expense):
            self.cursor.execute(
                "INSERT INTO expenses (amount, category, comment) VALUES (?, ?, ?)",
                (obj.amount, obj.category, obj.comment)
            )
            self.conn.commit()
            obj.pk = cast(int, self.cursor.lastrowid)
            return obj.pk

        raise TypeError("Unsupported object type")

    def get_category_by_name(self, name: str) -> Optional[Category]:
        """
        The get_category_by_name method takes in a name string as a parameter and returns
        either a Category object if a category with the given name exists in the
        categories table, or None otherwise.

        Parameters:

        name (str): The name of the category to be searched for in the database.

        Returns:

        Optional[Category]: If a category with the given name exists in the database,
            return a Category object with the primary key (pk), name, and parent category
            (if applicable) set to the corresponding values from the categories table.
            If a category with the given name does not exist in the database, return None
        """
        self.cursor.execute("SELECT * FROM categories WHERE name=?", (name,))
        row = self.cursor.fetchone()
        if row:
            return Category(pk=row[0], name=row[1], parent=row[2])
        return None

    def get(self, pk: int) -> Optional[T]:
        if self.model_class == Category:
            self.cursor.execute("SELECT * FROM categories WHERE pk=?", (pk,))
            row = self.cursor.fetchone()
            if row:
                return Category(pk=row[0], name=row[1], parent=row[2])
        elif self.model_class == Expense:
            self.cursor.execute("SELECT * FROM expenses WHERE pk=?", (pk,))
            row = self.cursor.fetchone()
            if row:
                return Expense(pk=row[0], amount=row[1], category=row[2],
                               expense_date=row[3], added_date=row[4], comment=row[5])

        return None

    def get_all(self, where: Optional[Dict[str, Any]] = None) -> List[T]:
        if self.model_class == Category:
            query = "SELECT * FROM categories"
            if where is not None:
                conditions = " AND ".join(f"{key} = ?" for key in where.keys())
                query += f" WHERE {conditions}"
                self.cursor.execute(query, tuple(where.values()))
            else:
                self.cursor.execute(query)
            return [Category(pk=row[0], name=row[1], parent=row[2])
                    for row in self.cursor.fetchall()]
        if self.model_class == Expense:
            query = "SELECT * FROM expenses"
            if where is not None:
                conditions = " AND ".join(f"{key} = ?" for key in where.keys())
                query += f" WHERE {conditions}"
                self.cursor.execute(query, tuple(where.values()))
            else:
                self.cursor.execute(query)
            return [Expense(pk=row[0], amount=row[1], category=row[2],
                            expense_date=row[3], added_date=row[4],
                            comment=row[5]) for row in self.cursor.fetchall()]

        return []

    def delete(self, pk: int) -> None:
        if self.model_class == Category:
            self.cursor.execute("DELETE FROM categories WHERE pk=?", (pk,))
            self.conn.commit()
        elif self.model_class == Expense:
            self.cursor.execute("DELETE FROM expenses WHERE pk=?", (pk,))
            self.conn.commit()
        else:
            raise TypeError("Unsupported object type")

    def update(self, obj: T) -> None:
        if isinstance(obj, Category):
            self.cursor.execute("UPDATE categories SET name=?, parent=? WHERE pk=?",
                                (obj.name, obj.parent, obj.pk))
            self.conn.commit()
        elif isinstance(obj, Expense):
            self.cursor.execute(
                "UPDATE expenses SET amount=?, category=?, comment=? WHERE pk=?",
                (obj.amount, obj.category, obj.comment, obj.pk)
            )
            self.conn.commit()
        else:
            raise TypeError("Unsupported object type")
