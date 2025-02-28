import inspect
import pathlib

import pytest
import sqlalchemy
from sqlalchemy import Column as SQLColumn, Integer

from schema_alchemist.utils import ImportPathResolver, TrieNode
from tests.test_utils.helpers import TestClass, Column


@pytest.mark.parametrize(
    "initial_values, expected_first_keys",
    [
        ([], ()),
        (["a.b.z"], [(["a", "b"], ["z"])]),
        (["a.b.z", "x.y.z"], [(["a"], ["b", "z"]), (["x"], ["y", "z"])]),
        (
            ["a.b.z", "x.y.z", "some.module.ClassName"],
            [
                (["a"], ["b", "z"]),
                (["x"], ["y", "z"]),
                (["some", "module"], ["ClassName"]),
            ],
        ),
        (
            [ImportPathResolver, "typing.Any", "src.utils.TrieNode"],
            [
                (["schema_alchemist", "utils"], ["ImportPathResolver"]),
                (["typing"], ["Any"]),
                (["src", "utils"], ["TrieNode"]),
            ],
        ),
    ],
)
def test_find_lcp_parts_for_import(initial_values, expected_first_keys):
    """
    Given multiple values to initialize the ImportPathResolver, ensure they are inserted correctly.
    """
    rt = ImportPathResolver(*initial_values)

    for i, v in enumerate(initial_values):
        if not isinstance(v, str):
            parts = rt.parts_of_import_path(v)
            v = parts.full_import_path
        assert rt.find_lcp_parts_for_import(v) == expected_first_keys[i]


@pytest.mark.parametrize(
    "value, expected",
    [
        ("my.module.path", {"module": "my.module.path", "main_class": "", "inner": ""}),
        (int, {"module": "", "main_class": "int", "inner": ""}),
        (str, {"module": "", "main_class": "str", "inner": ""}),
        (
            TestClass,
            {
                "module": "tests.test_utils.helpers",
                "main_class": "TestClass",
                "inner": "",
            },
        ),
        (
            TestClass.InnerClass,
            {
                "module": "tests.test_utils.helpers",
                "main_class": "TestClass",
                "inner": "InnerClass",
            },
        ),
        (
            ImportPathResolver,
            {
                "module": "schema_alchemist.utils",
                "main_class": "ImportPathResolver",
                "inner": "",
            },
        ),
    ],
)
def test_compute_import_path(value, expected):
    """
    Parametrized test for compute_import_path, verifying string/builtin logic.
    """
    result = ImportPathResolver.parts_of_import_path(value)
    assert result.module == expected["module"]
    assert result.main_class == expected["main_class"]
    assert result.inner == expected["inner"]


@pytest.mark.parametrize(
    "import_path, expected_prefix, expected_suffix",
    [
        ("", [], [""]),  # Empty path => no change
        ("myModule", [], ["myModule"]),
        ("a.b.z", ["a", "b"], ["z"]),
        ("x.y.z", ["x", "y"], ["z"]),
    ],
)
def test_split_prefix_suffix(
    import_path_resolver, import_path, expected_prefix, expected_suffix
):
    """
    Test the _split_prefix_suffix method with various import paths.
    """
    import_path_resolver.insert(import_path)
    prefix, suffix = import_path_resolver.find_lcp_parts_for_import(import_path)
    assert prefix == expected_prefix
    assert suffix == expected_suffix


@pytest.mark.parametrize(
    "value, expected",
    [
        (int, "int"),
        ("some.path", "path"),
        (TrieNode, "TrieNode"),
        (TestClass, "TestClass"),
        (TestClass.InnerClass, "TestClass.InnerClass"),
        (sqlalchemy, "sqlalchemy"),
        (Integer(), "Integer"),
    ],
)
def test_get_usage_name(import_path_resolver, value, expected):
    """
    Test extraction of minimal unique suffix for the given value's import path.
    """
    import_path_resolver.insert(value)
    result = import_path_resolver.get_usage_name(value)
    assert expected == result


def test_get_usage_same_name(import_path_resolver):
    import_path_resolver.insert_many(SQLColumn, Column)
    result = import_path_resolver.get_usage_name(SQLColumn)
    assert result == "schema_Column"
    result = import_path_resolver.get_usage_name(Column)
    assert result == "helpers_Column"


@pytest.mark.parametrize(
    "paths, reversed_tokens, expected_length",
    [
        (["a.b.c", "x.y.c"], ["c", "b", "a"], 2),
        (["a.b.c", "x.y.c"], ["c", "y", "x"], 2),
        (["single"], ["single"], 1),
    ],
)
def test_find_unique_suffix_length(paths, reversed_tokens, expected_length):
    rt = ImportPathResolver(*paths)
    assert rt._find_unique_suffix_length(reversed_tokens) == expected_length


def test_build_all_import_statements():
    inserts = [
        "a.b.z",
        "a.b.c",
        "d.b.c",
        "x.y.z",
        "simple",
        pathlib,
        "__file__.pathlib",
    ]
    expected = [
        "import pathlib as module_pathlib",
        "import simple",
        "from a.b import (\n    c as a_b_c,\n    z as b_z\n)",
        "from d.b import c as d_b_c",
        "from x.y import z as y_z",
    ]

    resolver = ImportPathResolver(*inserts)

    all_statements = resolver.build_all_import_statements()

    assert all_statements == expected


@pytest.mark.parametrize(
    "obj, expected",
    [
        (int, True),
        (42, True),
        ("42", False),
        (str, True),
        ("Exception", True),
        (Exception, True),
        ("", False),
        (inspect, False),
        ("inspect", False),
    ],
)
def test_is_builtin(obj, expected):
    assert ImportPathResolver.is_builtin_or_keyword(obj) == expected
