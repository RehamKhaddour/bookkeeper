"""
Виджет для отображения страницы списка расходов в окне приложения
"""
from datetime import datetime
from PySide6 import QtWidgets, QtCore
from dataclasses import dataclass
from typing import Callable, Optional

from bookkeeper.models.expense import Expense


expenses_example = [
    Expense(7.49, 'Хозтовары', 'Пакет на кассе'),
    ('2023-01-09 15:09:00', 139.99, 'Сыр', ''),
    ('2023-01-06 20:32:02', 5546.0, 'Книги', 'Книги по Python и pyqt'),
]

categories_example = "Продукты Сладости Книги Одежда".split()


class expensesList(QtWidgets.QWidget):
    def __init__(self, *args,
                 expenses_getter: Optional[Callable],
                 expenses_editor: Optional[Callable],
                 budgets_editor: Optional[Callable],
                 db_expense_getter: Optional[Callable],
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.editor = expenses_editor
        self.budgets_editor = budgets_editor
        self.db_expense_getter = db_expense_getter

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.expenses_title = QtWidgets.QLabel("Последние расходы")
        self.layout.addWidget(self.expenses_title)

        self.expenses_table = QtWidgets.QTableWidget(4, 20)
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(len(expenses_example))
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split()
        )
        self.header = self.expenses_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)

        self.set_expenses(expenses_getter)

    def build_expenses(self, data: list[Expense]) -> None:
        for i, row in enumerate(data):
            self.expenses_table.setItem(
                i, 0,
                QtWidgets.QTableWidgetItem(datetime.strptime(row.expense_date, "%Y-%m-%d %H:%M:%S").strftime("%d-%m-%Y"))
            )
            self.expenses_table.setItem(
                i, 1,
                QtWidgets.QTableWidgetItem(str(row.amount))
            )
            self.expenses_table.setItem(
                i, 2,
                QtWidgets.QTableWidgetItem(str(row.category).capitalize())
            )
            self.expenses_table.setItem(
                i, 3,
                QtWidgets.QTableWidgetItem(str(row.comment))
            )

    def set_expenses(self, expenses_getter: Callable) -> None:
        if self.expenses_table.itemAt(0, 0) is not None:
            self.expenses_table.setParent(None)

        expenses_data = expenses_getter()

        self.expenses_table = QtWidgets.QTableWidget(4, len(expenses_data))
        self.expenses_table.setColumnCount(4)
        self.expenses_table.setRowCount(len(expenses_data))
        self.expenses_table.setHorizontalHeaderLabels(
            "Дата Сумма Категория Комментарий".split()
        )
        self.header = self.expenses_table.horizontalHeader()
        self.header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        self.header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)

        self.build_expenses(expenses_data)
        self.expenses_table.itemChanged.connect(self.table_item_changed)
        self.layout.addWidget(self.expenses_table)

    @QtCore.Slot()
    def table_item_changed(self, item):
        table_position = self.expenses_table.indexFromItem(item)
        row, column = table_position.row(), table_position.column()

        pk = row + 1
        amount = float(self.expenses_table.item(row, 1).text())
        category = self.expenses_table.item(row, 2).text()
        expense_date = datetime.strptime(self.expenses_table.item(row, 0).text(), "%d-%m-%Y")
        comment = self.expenses_table.item(row, 3).text()
        if column == 1:
            old_value = self.db_expense_getter(pk)
            self.budgets_editor(value=-old_value.amount + amount, date=expense_date)
        print("table item changed: ",
              pk, " with amount ", amount,
              " and category ", category,
              " and expense date ", expense_date,
              " and comment ", comment)
        self.editor(pk, amount, category, expense_date, comment)


class addAmountElement(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.add_amount_input = QtWidgets.QLineEdit()
        self.add_amount_input.setPlaceholderText('Введите сумму, которую вы потратили')
        self.add_expense_date = QtWidgets.QLineEdit()
        self.add_expense_date.setPlaceholderText(
            'Формат: day-month-year'
        )

        self.layout.addWidget(self.add_amount_input)
        self.layout.addWidget(QtWidgets.QLabel("Дата покупки"))
        self.layout.addWidget(self.add_expense_date)


class chooseCategoryElement(QtWidgets.QWidget):
    def __init__(self, *args, category_list_getter: Callable, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.choose_category_label = QtWidgets.QLabel("Категория")
        self.layout.addWidget(self.choose_category_label)

        self.category_box = QtWidgets.QComboBox()
        self.update_categories(category_list_getter=category_list_getter)

    def update_categories(self, category_list_getter: Callable) -> None:
        self.category_box.setParent(None)

        self.category_box = QtWidgets.QComboBox()
        categories = category_list_getter()
        for category in categories:
            self.category_box.addItem(category)

        self.layout.addWidget(self.category_box)


class addCommentElement(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.add_comment_input = QtWidgets.QTextEdit()
        self.add_comment_input.setPlaceholderText('Введите комментарий')

        self.layout.addWidget(self.add_comment_input)


class elementAddExpense(QtWidgets.QWidget):
    def __init__(self, *args,
                 get_category_list: Callable,
                 adder: Callable,
                 budgets_editor: Callable,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.adder = adder
        self.budgets_editor = budgets_editor

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.add_expense_title = QtWidgets.QLabel("Добавить новую запись:")
        self.add_btn = QtWidgets.QPushButton(text="Добавить")
        self.add_btn.clicked.connect(self.save_btn_clicked)

        self.add_amount = addAmountElement()
        self.choose_category = chooseCategoryElement(category_list_getter=get_category_list)
        self.add_comment = addCommentElement()

        self.layout.addWidget(self.add_expense_title)
        self.layout.addWidget(self.add_amount)
        self.layout.addWidget(self.choose_category)
        self.layout.addWidget(self.add_comment)
        self.layout.addWidget(self.add_btn)

    @QtCore.Slot()
    def save_btn_clicked(self):
        amount = float(self.add_amount.add_amount_input.text())
        date = datetime.strptime(self.add_amount.add_expense_date.text(), "%d-%m-%Y")
        category = self.choose_category.category_box.currentText()
        comment = self.add_comment.add_comment_input.toPlainText()
        print("add expense:\namount ", amount,
              " date ", date, " category ", category,
              " comment ", comment)
        self.adder(amount, date, category, comment)
        self.budgets_editor(value=amount, date=date)


class expensesPage(QtWidgets.QWidget):
    def __init__(self, *args,
                 get_handler: Optional[Callable],
                 get_categories_handler: Optional[Callable],
                 add_handler: Optional[Callable],
                 edit_handler: Optional[Callable],
                 edit_budgets_handler: Optional[Callable],
                 get_db_expense_handler: Optional[Callable],
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.expenses_list = expensesList(
            expenses_getter=get_handler,
            expenses_editor=edit_handler,
            budgets_editor=edit_budgets_handler,
            db_expense_getter=get_db_expense_handler
        )
        self.layout.addWidget(self.expenses_list)

        self.add_expense = elementAddExpense(
            get_category_list=get_categories_handler,
            adder=add_handler,
            budgets_editor=edit_budgets_handler
        )
        self.layout.addWidget(self.add_expense)

