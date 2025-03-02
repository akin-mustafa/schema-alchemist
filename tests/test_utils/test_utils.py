import re
from enum import Enum
from typing import List

import pytest
from sqlalchemy import Column, INTEGER, Integer, ARRAY, VARCHAR, String

from schema_alchemist.constants import SQLRelationshipType
from schema_alchemist.utils import (
    create_table_name,
    convert_to_class_name,
    create_enum,
    inflect_engine,
    to_snake_case,
    to_camel_case,
    make_in_file_obj,
    resolve_column_type,
)


@pytest.mark.parametrize(
    "table, schema, expected",
    [
        ("users", None, "users"),
        ("users", "public", "public.users"),
        ("  users  ", "  public  ", "public.users"),
        ("users", "  public  ", "public.users"),
        ("  users  ", None, "users"),
    ],
)
def test_create_table_name(table, schema, expected):
    assert create_table_name(table, schema) == expected


@pytest.mark.parametrize(
    "table, schema, expected_exception",
    [
        ("", None, ValueError),
        ("   ", None, ValueError),
    ],
)
def test_create_table_name_invalid_inputs(table, schema, expected_exception):
    with pytest.raises(
        expected_exception, match="Table name cannot be empty or whitespace."
    ):
        create_table_name(table, schema)


@pytest.mark.parametrize(
    "input_str, expected_class_name",
    [
        ("hello world", "HelloWorld"),
        ("123hello world", "_123helloWorld"),
        ("hello@world!", "HelloWorld"),
        ("  multiple   spaces  ", "MultipleSpaces"),
        ("camelCaseTest", "CamelCaseTest"),
        ("platformDefinition", "PlatformDefinition"),
    ],
)
def test_to_class_name(input_str, expected_class_name):
    assert convert_to_class_name(input_str) == expected_class_name


@pytest.mark.parametrize(
    "input_str, message",
    [
        (None, "Invalid argument type: NoneType"),
        ("", "Class name cannot be empty."),
        ("", "Class name cannot be empty."),
        ("   ", "Class name cannot be empty."),
        ("$%^&", "Class name cannot be empty."),
        (Column, "Invalid argument type: Column"),
    ],
)
def test_to_class_name_fail(input_str, message):
    error_msg = re.escape(message)
    with pytest.raises(ValueError, match=error_msg):
        convert_to_class_name(input_str)


def test_create_enum():
    Color = create_enum("Color", ["RED", "GREEN", "BLUE"])
    assert isinstance(Color, type) and issubclass(Color, Enum)
    assert Color.RED.name == "RED"
    assert Color.GREEN.name == "GREEN"
    assert Color.BLUE.name == "BLUE"

    assert Color.RED.value == "RED"
    assert Color.GREEN.value == "GREEN"
    assert Color.BLUE.value == "BLUE"


@pytest.mark.parametrize(
    "word, expected",
    [
        ("apples", "apple"),
        ("apple", "apple"),
        ("children", "child"),
        ("sheep", "sheep"),
    ],
)
def test_to_singular(word, expected):
    assert inflect_engine.to_singular(word) == expected


@pytest.mark.parametrize(
    "word, expected",
    [
        ("apple", "apples"),
        ("apples", "apples"),
        ("boats", "boats"),
        ("child", "children"),
        ("sheep", "sheep"),
    ],
)
def test_to_plural(word, expected):
    assert inflect_engine.to_plural(word) == expected


@pytest.mark.parametrize(
    "relationship, expected",
    [
        (SQLRelationshipType.m2o, SQLRelationshipType.o2m),
        (SQLRelationshipType.o2m, SQLRelationshipType.m2o),
        (SQLRelationshipType.m2m, SQLRelationshipType.m2m),
        (SQLRelationshipType.o2o, SQLRelationshipType.o2o),
    ],
)
def test_reversed_relationship(relationship, expected):
    assert relationship.reversed_relationship == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("thisIsATest", "this_is_a_test"),
        ("this is a test", "this_is_a_test"),
        ("this-is-a-test", "this_is_a_test"),
        ("ThisIsATest", "this_is_a_test"),
        ("anotherTestString", "another_test_string"),
        ("Already_Snake_Case", "already_snake_case"),
        ("JSONResponseData", "json_response_data"),
    ],
)
def test_to_snake_case(input_str, expected):
    assert to_snake_case(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("this_is_a_test", "thisIsATest"),
        ("this-is-a-test", "thisIsATest"),
        ("this is a test", "thisIsATest"),
        ("alreadyCamelCase", "alreadyCamelCase"),
        ("AlreadyCamelCase", "alreadyCamelCase"),
        ("Another_example_string", "anotherExampleString"),
        ("json_response_data", "jsonResponseData"),
    ],
)
def test_to_camel_case(input_str, expected):
    assert to_camel_case(input_str) == expected


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("test", "__file__.test"),
        (int, "__file__.int"),  # when given a class, it returns __file__.<ClassName>
    ],
)
def test_make_in_file_obj(input_val, expected):
    result = make_in_file_obj(input_val)
    assert result == expected


@pytest.mark.parametrize(
    "data, expected_sql_types, expected_sql_generic_types, expected_python_types",
    (
        ({"name": "test", "type": INTEGER()}, (INTEGER,), (Integer,), (int,)),
        (
            {"name": "test", "type": ARRAY(VARCHAR())},
            (
                VARCHAR,
                ARRAY,
            ),
            (
                ARRAY,
                String,
            ),
            (List, str),
        ),
    ),
)
def test_resolve_column_type(
    data, expected_sql_types, expected_sql_generic_types, expected_python_types
):
    result = resolve_column_type(data, "test")
    assert set(result.sql_types) == set(expected_sql_types)
    assert set(result.sql_generic_types) == set(expected_sql_generic_types)
    assert set(result.python_types) == set(expected_python_types)
