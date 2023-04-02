import os
import tempfile
import pytest

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.sqlite_repository import SqliteRepository


@pytest.fixture(scope="module")
def sqlite_category_repo():
    # create a temporary database file for testing categories
    with tempfile.NamedTemporaryFile(suffix='.db', dir='tests/test_repository/temp',
                                     mode='w', delete=False) as tmpdir:
        db_path = tmpdir.name

    # create a SqliteRepository instance with Category model
    repo = SqliteRepository(db_path, Category)

    yield repo


@pytest.fixture(scope="module")
def sqlite_expense_repo():
    # create a temporary database file for testing expenses
    with tempfile.NamedTemporaryFile(suffix='.db', dir='tests/test_repository/temp',
                                     mode='w',delete=False) as tmpdir:
        db_path = tmpdir.name

    # create a SqliteRepository instance with Expense model
    repo = SqliteRepository(db_path, Expense)

    yield repo

def test_add_category(sqlite_category_repo):
    # add a category to the database
    category = Category(name="Food", parent=None)
    pk = sqlite_category_repo.add(category)

    # check that the category was added with the correct pk
    assert pk == 1

    # add another category with the same name, should return the existing pk
    category2 = Category(name="Food", parent=None)
    pk2 = sqlite_category_repo.add(category2)
    assert pk2 == 1

    # add a category with a parent
    category3 = Category(name="Fruits", parent=pk)
    pk3 = sqlite_category_repo.add(category3)
    assert pk3 == 2


def test_get_category_by_name(sqlite_category_repo):
    # add some categories to the database
    category1 = Category(name="Food", parent=None)
    category2 = Category(name="Fruits", parent=1)
    sqlite_category_repo.add(category1)
    sqlite_category_repo.add(category2)

    # get a category by name
    found_category = sqlite_category_repo.get_category_by_name("Fruits")

    # check that the correct category was found
    assert found_category.name == "Fruits"
    assert found_category.parent == 1

def test_get_all_categories(sqlite_category_repo):
    # add some categories to the repository
    categories = [
        Category(name="Food", parent=None),
        Category(name="Fruits", parent=1),
        Category(name="Vegetables", parent=1),
    ]
    for category in categories:
        sqlite_category_repo.add(category)

    # get all categories
    all_categories = sqlite_category_repo.get_all()

    # check that the correct number of categories were retrieved
    assert len(all_categories) == 3

    # check that each category has the correct attributes
    assert all_categories[0].name == "Food"
    assert all_categories[0].parent is None

    assert all_categories[1].name == "Fruits"
    assert all_categories[1].parent == 1

    assert all_categories[2].name == "Vegetables"
    assert all_categories[2].parent == 1

def test_update_category(sqlite_category_repo):
    # add a category
    category = Category(name="Test category")
    category_pk = sqlite_category_repo.add(category)

    # update the category
    category.name = "Updated category"
    sqlite_category_repo.update(category)

    # check if the category was updated
    updated_category = sqlite_category_repo.get(category_pk)
    assert updated_category is not None
    assert updated_category.name == "Updated category"

def test_delete_category(sqlite_category_repo):
    # add a category
    category = Category(name="Test category")
    category_pk = sqlite_category_repo.add(category)

    # delete the category
    sqlite_category_repo.delete(category_pk)

    # check if the category was deleted
    assert sqlite_category_repo.get(category_pk) is None

def test_add_expense(sqlite_expense_repo):
    # add an expense to the database
    expense = Expense(amount=50, category=1)
    pk = sqlite_expense_repo.add(expense)

    # check that the expense was added with the correct pk
    assert pk == 1

    # add another expense with a different amount and category_id
    expense2 = Expense(amount=20, category=2)
    pk2 = sqlite_expense_repo.add(expense2)
    assert pk2 == 2
    sqlite_expense_repo.delete(pk)
    sqlite_expense_repo.delete(pk2)

def test_get_expense(sqlite_expense_repo):
    # add an expense to the database
    expense = Expense(amount=50, category=1, comment="Lunch")
    pk = sqlite_expense_repo.add(expense)

    # get the expense by pk
    found_expense = sqlite_expense_repo.get(pk)

    # check that the correct expense was found
    assert found_expense.amount == 50
    assert found_expense.category == 1
    assert found_expense.comment == "Lunch"
    sqlite_expense_repo.delete(pk)

def test_get_all_expenses(sqlite_expense_repo):
    # add some expenses to the repository
    expenses = [
        Expense(amount=100, category=1, comment="expense 1"),
        Expense(amount=200, category=1, comment="expense 2"),
        Expense(amount=300, category=2, comment="expense 3"),
    ]
    for expense in expenses:
        sqlite_expense_repo.add(expense)

    # get all expenses
    all_expenses = sqlite_expense_repo.get_all()

    # check that the correct number of expenses were retrieved
    assert len(all_expenses) == 3

    # check that each expense has the correct attributes
    assert all_expenses[0].amount == 100
    assert all_expenses[0].category == 1
    assert all_expenses[0].comment == "expense 1"

    assert all_expenses[1].amount == 200
    assert all_expenses[1].category == 1
    assert all_expenses[1].comment == "expense 2"

    assert all_expenses[2].amount == 300
    assert all_expenses[2].category == 2
    assert all_expenses[2].comment == "expense 3"

def test_update_expense(sqlite_expense_repo):
    # add an expense to the repository
    expense = Expense(amount=100, category=1, comment="test expense")
    pk = sqlite_expense_repo.add(expense)

    # update the expense
    expense.amount = 200
    expense.comment = "updated expense"
    sqlite_expense_repo.update(expense)

    # check that the updated expense has the correct values
    updated_expense = sqlite_expense_repo.get(pk)
    assert updated_expense.amount == 200
    assert updated_expense.comment == "updated expense"
    sqlite_expense_repo.delete(pk)

def test_delete_expense(sqlite_expense_repo):
    # add an expense to the database
    expense = Expense(amount=50, category=1, comment="Lunch")
    pk = sqlite_expense_repo.add(expense)

    # delete the expense by pk
    sqlite_expense_repo.delete(pk)

    # try to get the expense by pk, should return None
    found_expense = sqlite_expense_repo.get(pk)
    assert found_expense is None