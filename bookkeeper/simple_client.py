"""
Простой тестовый скрипт для терминала
"""

from bookkeeper.models.category import Category
from bookkeeper.models.expense import Expense
from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.repository.sqlite_repository import SqliteRepository
from bookkeeper.utils import read_tree

MODE = 'Sqlite'
CAT_REPO = None
EXP_REPO = None

if MODE == 'Memory':
    CAT_REPO = MemoryRepository[Category]()
    EXP_REPO = MemoryRepository[Expense]()
elif MODE == 'Sqlite':
    DB_PATH_NAME = 'bookkeeper/databases/test.db'
    CAT_REPO = SqliteRepository(DB_PATH_NAME, Category)
    EXP_REPO = SqliteRepository(DB_PATH_NAME, Expense)


cats = '''
продукты
    мясо
        сырое мясо
        мясные продукты
    сладости
книги
одежда
'''.splitlines()

Category.create_from_tree(read_tree(cats), CAT_REPO)

while True:
    try:
        cmd = input('$> ')
    except EOFError:
        break
    if not cmd:
        continue
    if cmd == 'категории':
        print(*CAT_REPO.get_all(), sep='\n')
    elif cmd == 'расходы':
        print(*EXP_REPO.get_all(), sep='\n')
    elif cmd[0].isdecimal():
        amount, name = cmd.split(maxsplit=1)
        try:
            cat = CAT_REPO.get_all({'name': name})[0]
        except IndexError:
            print(f'категория {name} не найдена')
            continue
        exp = Expense(int(amount), cat.pk)
        EXP_REPO.add(exp)
        print(exp)
