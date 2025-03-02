from enum import Enum

import pytest

from sqlalchemy import Enum as SqlAlchemyEnum

from schema_alchemist.generators import EnumGenerator
from schema_alchemist.utils import DEFAULT_INDENTATION


def test_enum_generator_init(import_path_resolver):
    name = "status"
    items = ["active", "inactive", "suspended"]

    eg = EnumGenerator(name, items, import_path_resolver)

    assert eg.name == name
    assert eg.items == items
    assert eg.import_path_resolver == import_path_resolver
    assert eg.indentation == DEFAULT_INDENTATION

    indentation = " "
    eg = EnumGenerator(name, items, import_path_resolver, indentation)
    assert eg.indentation == indentation


@pytest.mark.parametrize(
    "name, items, expected",
    (
        (
            "status",
            ["active", "inactive", "suspended"],
            (
                "class status(Enum):\n"
                "    active = 'active'\n"
                "    inactive = 'inactive'\n"
                "    suspended = 'suspended'"
            ),
        ),
        (
            "SwitchEnum",
            ["open", "closed", "test this"],
            "class SwitchEnum(Enum):\n    open_ = 'open'\n    closed = 'closed'\n    "
            "test_this = 'test this'",
        ),
    ),
)
def test_enum_generator_generate(name, items, expected, import_path_resolver):
    import_path_resolver.insert_many(Enum)
    eg = EnumGenerator(name, items, import_path_resolver)
    assert eg.generate() == expected


def test_enum_generator_generate_with_usage(import_path_resolver):
    name = "status"
    items = ["active", "inactive", "suspended"]

    expected = (
        "class status(enum_Enum):\n"
        "    active = 'active'\n"
        "    inactive = 'inactive'\n"
        "    suspended = 'suspended'"
    )

    import_path_resolver.insert_many(SqlAlchemyEnum, Enum)

    eg = EnumGenerator(name, items, import_path_resolver)

    assert eg.generate() == expected
