from dataclasses import dataclass

from bookkeeper.repository.sqlite_repository import SQLiteRepository
import pytest


TEST_DB = 'bookkeeper/databases/test.sqlite.db'


@pytest.fixture
def test_class():
    @dataclass
    class Custom:
        pk: int = 0
        f: int = 1
    return Custom


@pytest.fixture
def repos(test_class):
    repos = SQLiteRepository.repository_factory(models=[test_class], db_file=TEST_DB)
    return repos


@pytest.fixture
def repo(repos, test_class):
    repo = repos[test_class]
    return repo


def test_repo_factory(repos, test_class):
    assert repos[test_class].db_file == TEST_DB \
           and repos[test_class].table_name == test_class.__name__.lower()


def test_crud(repo, test_class):
    obj = test_class(f=2)
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk) == obj
    obj2 = test_class()
    obj2.pk = pk
    repo.update(obj2)
    assert repo.get(pk) == obj2
    obj3 = test_class(f=10)
    repo.add(obj3)
    assert repo.get_all() == [obj2, obj3]
    repo.delete(pk)
    assert repo.get(pk) is None
    repo.delete(2)


def test_cannot_add_with_pk(repo, test_class):
    obj = test_class(f=3)
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_update_without_pk(repo, test_class):
    obj = test_class(f=4)
    with pytest.raises(ValueError):
        repo.update(obj)


def test_get_all(repo, test_class):
    objects = [test_class(f=i+21) for i in range(5)]
    for o in objects:
        repo.add(o)
    assert repo.get_all() == objects


def test_get_all_with_condition(repo, test_class):
    objects = [test_class(f=20) for i in range(5)]
    objects_2 = [test_class(f=10) for i in range(5)]
    for o in objects:
        repo.add(o)
    for o in objects_2:
        repo.add(o)
    assert repo.get_all(where={"f": 20}) == objects
    assert repo.get_all(where={"f": 10}) == objects_2


def test_drop_tables_in_repos(repos):
    for cls, repo in repos.items():
        repo.drop_table()
