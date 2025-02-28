import os.path

import pytest
from sqlalchemy import Column
from sqlalchemy.orm import mapped_column

from schema_alchemist.utils import StringReprWrapper, DEFAULT_INDENTATION
from tests.test_generators.conftest import DummyGenerator


@pytest.mark.parametrize(
    "func, parameters, positional_args, expected",
    (
        (
            Column,
            {
                "name": "id",
                "type_": StringReprWrapper("Integer"),
                "index": None,  # default value, will be ignored
                "primary_key": True,
            },
            ["name", "type_"],
            "Column('id', Integer, primary_key=True)",
        ),
        (
            Column,
            {
                "name": "id",
                "type_": StringReprWrapper("Integer"),
                "index": None,  # default value, will be ignored
                "primary_key": True,
            },
            None,  # don't override positional args,
            "Column(name='id', type_=Integer, primary_key=True)",
        ),
        (
            mapped_column,
            {
                "name": "id",
                "type_": StringReprWrapper("Integer"),
                "index": None,  # default value, will be ignored
                "primary_key": True,
            },
            ["name", "type_"],
            "mapped_column('id', Integer, primary_key=True)",
        ),
        (
            mapped_column,
            {
                "name": "id",
                "type_": StringReprWrapper("Integer"),
                "index": None,  # default value, will be ignored
                "primary_key": True,
            },
            None,  # don't override positional args,
            "mapped_column(primary_key=True, name='id', type_=Integer)",
        ),
        (
            os.path.join,
            {
                "a": "foo",
                "p": ["bar", "baz"],  # star args
            },
            None,
            "join('foo', 'bar', 'baz')",
        ),
    ),
)
def test_generate_function_definition(
    func, parameters, positional_args, expected, dummy_generator
):
    dummy_generator.import_path_resolver.insert(func)
    func_def = dummy_generator.generate_function_definition(
        func,
        parameters,
        positional_args,
    )
    assert func_def == expected


def test_default_indent(dummy_generator):
    assert dummy_generator.default_indentation == DEFAULT_INDENTATION


def test_indentation_assignment(import_path_resolver):
    gen = DummyGenerator(import_path_resolver=import_path_resolver, indentation="    ")
    assert gen.indentation == "    "
    gen2 = DummyGenerator(import_path_resolver=import_path_resolver)
    assert gen2.indentation is None
