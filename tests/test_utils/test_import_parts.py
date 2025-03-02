import os
import pytest

from sqlalchemy import Column
from schema_alchemist.utils import ImportParts, empty
from tests.test_utils.helpers import TestClass, outer_func


@pytest.mark.parametrize(
    "obj, expected_full_import, expected_qualified_name, expected_has_inner",
    [
        (
            TestClass.InnerClass,
            "tests.test_utils.helpers.TestClass",
            "TestClass.InnerClass",
            True,
        ),
        (TestClass, "tests.test_utils.helpers.TestClass", "TestClass", False),
        (outer_func, "tests.test_utils.helpers.outer_func", "outer_func", False),
        (os, "os", "", False),
        ("package.test", "package.test", "", False),
    ],
)
def test_import_parts(
    obj, expected_full_import, expected_qualified_name, expected_has_inner
):
    parts = ImportParts(obj)
    assert parts.full_import_path == expected_full_import
    assert parts.qualified_name == expected_qualified_name

    assert parts.has_inner_inner is expected_has_inner


@pytest.mark.parametrize(
    "obj, alias, expected_usage",
    [
        (TestClass.InnerClass, "TestClass", "TestClass.InnerClass"),
        (TestClass.InnerClass, "", "TestClass.InnerClass"),
        (TestClass, "TestClass", "TestClass"),
        (TestClass, "", "TestClass"),
        (TestClass.InnerClass, "Alias", "Alias.InnerClass"),
        (TestClass, "Alias", "Alias"),
        (TestClass.InnerClass, None, "TestClass.InnerClass"),
        (TestClass, None, "TestClass"),
    ],
)
def test_get_usage(obj, alias, expected_usage):
    parts = ImportParts(obj)
    assert parts.get_usage(alias) == expected_usage


@pytest.mark.parametrize(
    "data, expected",
    (
        (os, ("os", empty)),
        ("test_string", ("builtins", str)),
        (Column, ("sqlalchemy.sql.schema", Column)),
    ),
)
def test_get_module_and_class(data, expected):
    assert ImportParts.get_module_and_class(data) == expected
