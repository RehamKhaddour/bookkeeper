"""
Вспомогательные функции
"""

from typing import Iterable, Iterator


def _get_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _lines_with_indent(lines: Iterable[str]) -> Iterator[tuple[int, str]]:
    for line in lines:
        if not line or line.isspace():
            continue
        yield _get_indent(line), line.strip()


def read_tree(lines: Iterable[str]) -> list[tuple[str, str | None]]:
    """
    Прочитать структуру дерева из текста на основе отступов. Вернуть список
    пар "потомок-родитель" в порядке топологической сортировки. Родитель
    элемента верхнего уровня - None.

    Пример. Следующий текст:
    parent
        child1
            child2
        child3

    даст такое дерево:
    [('parent', None), ('child1', 'parent'),
     ('child2', 'child1'), ('child3', 'parent')]

    Пустые строки игнорируются.

    Parameters
    ----------
    lines - Итерируемый объект, содержащий строки текста (файл или список строк)

    Returns
    -------
    Список пар "потомок-родитель"
    """
    parents: list[tuple[str | None, int]] = []
    last_indent = -1
    last_name = None
    result: list[tuple[str, str | None]] = []
    for i, (indent, name) in enumerate(_lines_with_indent(lines)):
        if indent > last_indent:
            parents.append((last_name, last_indent))
        elif indent < last_indent:
            while indent < last_indent:
                _, last_indent = parents.pop()
            if indent != last_indent:
                raise IndentationError(
                    f'unindent does not match any outer indentation '
                    f'level in line {i}:\n'
                )
        result.append((name, parents[-1][0]))
        last_name = name
        last_indent = indent
    return result


def build_dict_tree_from_list(sorted_list: list) -> dict:
    """
    Функция строит из массива записей вида (имя, родительский id, id)
    дерево с json-подобной структурой (ключи - id)
    """
    tree = {}
    for element in sorted_list:
        set_elem_in_tree(tree, element)
    return tree


def get_elem_in_tree(tree: dict, pk: int) -> list:
    """
    Функция по id элемента ищет его в json-like дереве
    """
    for key, value in tree.items():
        if key != pk and isinstance(key, int):
            item = get_elem_in_tree(value, pk)
            if item is not None:
                return item
        elif key == pk:
            return value


def get_elem_parent(tree: dict, pk: int, prev_parent: int = None) -> int:
    """
    Функция по id элемента ищет id его родителя в json-like дереве
    """
    for key, value in tree.items():
        if key != pk and isinstance(key, int):
            parent = get_elem_parent(value, pk, key)
            if parent is not None:
                return parent
        elif key == pk:
            return prev_parent


def set_elem_in_tree(tree: dict, elem: list[type]) -> None:
    """
    Функция по заданной записи вида (имя, родительский id, id) меняет элемент в дереве
    """
    if elem.parent is None:
        tree[elem.pk] = {"name": elem.name}
    else:
        if isinstance(tree, dict):
            for key, value in tree.items():
                if key != elem.parent:
                    set_elem_in_tree(value, elem)
                else:
                    value[elem.pk] = {"name": elem.name}
                    break


def delete_elem_from_tree(tree: dict, pk: int) -> None:
    """
    Функция по id элемента удаляет его из json-like дерева
    """
    for key, value in tree.items():
        if key != pk and isinstance(key, int):
            delete_elem_from_tree(value, pk)
        elif key == pk:
            del tree[key]
            break


if __name__ == "__main__":
    example = [
        ["продукты", None, 1],
        ["мясо", 1, 2],
        ["сырое мясо", 2, 3],
        ["мясные продукты", 2, 4],
        ["сладости", 1, 5],
        ["книги", None, 6],
        ["одежда", None, 7],
    ]

    sample_tree = build_dict_tree_from_list(example)
    set_elem_in_tree(sample_tree, ['почта', 5, 8])
    set_elem_in_tree(sample_tree, ['пицца', 5, 8])
    print(get_elem_parent(sample_tree, 6))
    print(get_elem_in_tree(sample_tree, 8))
    delete_elem_from_tree(sample_tree, 2)
    print(sample_tree)
