"""
Класс приложения на PyQT (view)
"""
import sys
from PySide6 import QtWidgets
from functools import partial
from typing import Optional, Callable

from bookkeeper.view.expenses_page import expensesPage
from bookkeeper.view.categories_page import categoriesPage
from bookkeeper.view.budget_page import BudgetPage

categories_example = {
    1: {
        "name": "продукты",
        2: {
            "name": "мясо",
            3: {
                "name": "сырое мясо"
            },
            4: {
                "name": "мясные продукты"
            }
        },
        5: {
            "name": "сладости"
        }
    },
    6: {
        "name": "книги"
    },
    7: {
        "name": "одежда"
    },
    8: {
        "name": "почта"
    }
}


def get_example():
    return categories_example


def handle_error(widget, handler):
    def inner(*args, **kwargs):
        try:
            handler(*args, **kwargs)
        except Exception as ex:
            QtWidgets.QMessageBox.critical(widget, 'Ошибка', str(ex))

    return inner


class pageManagerToolbar(QtWidgets.QWidget):
    def __init__(self, *args, parent: type | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.parent = parent

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.expensesBtn = QtWidgets.QPushButton(text="Расходы")
        self.expensesBtn.clicked.connect(partial(self.set_page, 0))
        self.layout.addWidget(self.expensesBtn)

        self.budgetBtn = QtWidgets.QPushButton(text="Бюджет")
        self.budgetBtn.clicked.connect(partial(self.set_page, 1))
        self.layout.addWidget(self.budgetBtn)

        self.categoriesBtn = QtWidgets.QPushButton(text="Категории расходов")
        self.categoriesBtn.clicked.connect(partial(self.set_page, 2))
        self.layout.addWidget(self.categoriesBtn)

    def set_page(self, page_index=0) -> None:
        self.parent.page_layout.setCurrentIndex(page_index)
        # print("button was clicked: ", str(self.parent.page_layout.currentIndex()))


class MainWindow(QtWidgets.QWidget):
    get_category_handler: Optional[Callable]
    add_category_handler: Optional[Callable]
    edit_category_handler: Optional[Callable]
    delete_category_handler: Optional[Callable]

    get_expenses_handler: Optional[Callable]
    get_categories_handler: Optional[Callable]
    add_expense_handler: Optional[Callable]
    edit_expense_handler: Optional[Callable]
    edit_budgets_handler: Optional[Callable]
    get_db_expense_handler: Optional[Callable]

    get_budgets_handler: Optional[Callable]
    set_budgets_handler: Optional[Callable]

    def __init__(self, *args,
                 category_handlers: list[Optional[Callable]],
                 expenses_handlers: list[Optional[Callable]],
                 budgets_handlers: list[Optional[Callable]],
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.register_category_handlers(category_handlers)
        self.register_expenses_handlers(expenses_handlers)
        self.register_budgets_handlers(budgets_handlers)

        self.setWindowTitle("The BookKeeper App")
        self.setGeometry(50, 50, 800, 900)

        self.budget_page = BudgetPage(
            get_handler=self.get_budgets_handler,
            set_handler=self.set_budgets_handler
        )
        self.expenses_page = expensesPage(
            get_handler=self.get_expenses_handler,
            get_categories_handler=self.get_categories_handler,
            add_handler=self.add_expense_handler,
            edit_handler=self.edit_expense_handler,
            edit_budgets_handler=self.edit_budgets_handler,
            get_db_expense_handler=self.get_db_expense_handler
        )
        self.categories_page = categoriesPage(
            get_handler=self.get_category_handler,
            add_handler=self.add_category_handler,
            edit_handler=self.edit_category_handler,
            delete_handler=self.delete_category_handler
        )
        self.menuBarWidget = pageManagerToolbar(parent=self)

        self.layout = QtWidgets.QVBoxLayout()

        self.page_layout = QtWidgets.QStackedLayout()
        self.page_layout.addWidget(self.expenses_page)
        self.page_layout.addWidget(self.budget_page)
        self.page_layout.addWidget(self.categories_page)

        self.layout.addWidget(self.menuBarWidget)
        self.layout.addLayout(self.page_layout)
        self.setLayout(self.layout)

    def register_category_handlers(self, handlers: list[Optional[Callable]]) -> None:
        self.get_category_handler = handlers[0]
        self.add_category_handler = handlers[1]
        self.edit_category_handler = handlers[2]
        self.delete_category_handler = handlers[3]

    def register_expenses_handlers(self, handlers: list[Optional[Callable]]) -> None:
        self.get_expenses_handler = handlers[0]
        self.get_categories_handler = handlers[1]
        self.add_expense_handler = handlers[2]
        self.edit_expense_handler = handlers[3]
        self.edit_budgets_handler = handlers[4]
        self.get_db_expense_handler = handlers[5]

    def register_budgets_handlers(self, handlers: list[Optional[Callable]]) -> None:
        self.get_budgets_handler = handlers[0]
        self.set_budgets_handler = handlers[1]


class View:
    app: QtWidgets.QApplication
    window: MainWindow
    category_handlers: list[Optional[Callable]]
    expenses_handlers: list[Optional[Callable]]
    budgets_handlers: list[Optional[Callable]]

    def __init__(self) -> None:
        self.app = QtWidgets.QApplication(sys.argv)

    def start_app(self) -> None:
        self.window = MainWindow(
            category_handlers=self.category_handlers,
            expenses_handlers=self.expenses_handlers,
            budgets_handlers=self.budgets_handlers
        )
        self.window.show()
        sys.exit(self.app.exec())

    def register_handlers(self, handlers_obj: dict[str, list[Optional[Callable]]]):
        self.category_handlers = handlers_obj["category"]
        self.expenses_handlers = handlers_obj["expenses"]
        self.budgets_handlers = handlers_obj["budget"]
