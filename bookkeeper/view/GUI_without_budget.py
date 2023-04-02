from typing import Optional
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QFormLayout,
    QLineEdit,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QDialog,
    QDialogButtonBox,
    QComboBox,
    QInputDialog,
    QTreeWidget,
    QTreeWidgetItem
)
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense


class AddExpenseForm(QDialog):
    def __init__(self, repository: SqliteRepository, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.amount_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.comment_edit = QLineEdit()
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.init_ui()
        self.load_categories()

    def init_ui(self):
        layout = QFormLayout()
        layout.addRow("Amount:", self.amount_edit)
        layout.addRow("Category:", self.category_combo)
        layout.addRow("Comment:", self.comment_edit)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def load_categories(self):
        self.category_combo.clear()
        categories = self.repository.get_all(Category)
        for category in categories:
            self.category_combo.addItem(category.name, category.pk)

    def get_expense(self) -> Optional[Expense]:
        amount = self.amount_edit.text().strip()
        category_pk = self.category_combo.currentData()
        comment = self.comment_edit.text().strip()
        if not amount or not category_pk:
            return None
        expense = Expense(amount=int(amount), category=int(category_pk))
        if comment:
            expense.comment = comment
        return expense


class ManageCategoriesForm(QDialog):
    def __init__(self, repository: SqliteRepository, parent=None):
        super().__init__(parent)
        self.repository = repository
        self.categories_list = QListWidget()
        self.new_category_edit = QLineEdit()
        self.parent_category_combo = QComboBox()
        self.new_category_button = QPushButton("Add")
        self.delete_category_button = QPushButton("Delete")
        self.edit_category_button = QPushButton("Edit")
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.init_ui()
        self.load_categories()

    def init_ui(self):
        layout = QVBoxLayout()

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.new_category_edit)
        buttons_layout.addWidget(self.parent_category_combo)
        buttons_layout.addWidget(self.new_category_button)

        edit_buttons_layout = QHBoxLayout()
        edit_buttons_layout.addWidget(self.edit_category_button)
        edit_buttons_layout.addWidget(self.delete_category_button)

        layout.addWidget(self.categories_list)
        layout.addLayout(buttons_layout)
        layout.addLayout(edit_buttons_layout)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.new_category_button.clicked.connect(self.add_category)
        self.edit_category_button.clicked.connect(self.edit_category)
        self.delete_category_button.clicked.connect(self.delete_category)

    def load_categories(self):
        self.categories_list.clear()
        categories = self.repository.get_all(Category)
        for category in categories:
            item = QListWidgetItem(category.name)
            item.setData(Category, category)
            self.categories_list.addItem(item)
        self.load_parent_categories()

    def load_parent_categories(self):
        self.parent_category_combo.clear()
        categories = self.repository.get_all(Category)
        self.parent_category_combo.addItem("No parent category", None)
        for category in categories:
            self.parent_category_combo.addItem(category.name, category.pk)

    def add_category(self):
        name = self.new_category_edit.text().strip()
        parent_pk = self.parent_category_combo.currentData()
        if name:
            category = Category(name=name)
            if parent_pk:
                category.parent_category = int(parent_pk)
            self.repository.save(category)
            self.load_categories()
            self.new_category_edit.clear()

    def edit_category(self):
        selected_item = self.categories_list.currentItem()
        if not selected_item:
            return
        category = selected_item.data(Category)
        name, ok = QInputDialog.getText(self, "Edit Category", "Category Name:", QLineEdit.Normal, category.name)
        if ok and name:
            category.name = name
            parent_pk = self.parent_category_combo.currentData()
            if parent_pk:
                category.parent_category = int(parent_pk)
            self.repository.save(category)
            selected_item.setText(category.name)

    def delete_category(self):
        selected_item = self.categories_list.currentItem()
        if not selected_item:
            return
        category = selected_item.data(Category)
        self.repository.delete(category)
        self.load_categories()

class MainWindow(QMainWindow):
    def init(self, repository: SqliteRepository):
        super().init()
        self.repository = repository
        self.expenses_list = QListWidget()
        self.categories_tree = QTreeWidget()
        self.categories_tree.setColumnCount(2)
        self.categories_tree.setHeaderLabels(["Category", "Total Amount"])

        self.add_expense_button = QPushButton("Add Expense")
        self.manage_categories_button = QPushButton("Manage Categories")

        self.init_ui()
        self.load_expenses()
        self.load_categories()

    def init_ui(self):
        central_widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(self.expenses_list)
        layout.addWidget(self.categories_tree)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_expense_button)
        buttons_layout.addWidget(self.manage_categories_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(buttons_layout)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.add_expense_button.clicked.connect(self.add_expense)
        self.manage_categories_button.clicked.connect(self.manage_categories)

        self.setWindowTitle("Bookkeeper")

    def load_expenses(self):
        self.expenses_list.clear()
        expenses = self.repository.get_all(Expense, order_by="-created_at")
        for expense in expenses:
            item = QListWidgetItem(f"{expense.amount} - {expense.category_name}")
            item.setData(Expense, expense)
            self.expenses_list.addItem(item)

    def load_categories(self):
        self.categories_tree.clear()
        categories = self.repository.get_all(Category, order_by="name")
        top_level_items = []
        for category in categories:
            if category.parent_category:
                continue
            item = QTreeWidgetItem([category.name, ""])
            self.categories_tree.addTopLevelItem(item)
            top_level_items.append(item)
        for item in top_level_items:
            self.load_child_categories(item)

    def load_child_categories(self, parent_item):
        category = parent_item.data(0, Category)
        children = category.children.all()
        for child in children:
            item = QTreeWidgetItem([child.name, ""])
            parent_item.addChild(item)
            self.load_child_categories(item)

    def add_expense(self):
        form = AddExpenseForm(self.repository, self)
        if form.exec() == QDialog.Accepted:
            expense = form.get_expense()
            if expense:
                self.repository.save(expense)

if __name__ == '__main__':
    app = QApplication([])
    DB_PATH_NAME = 'bookkeeper/databases/test.db'
    window = MainWindow()
    window.show()
    app.exec()