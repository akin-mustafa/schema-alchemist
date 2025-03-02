from unittest.mock import patch

import pytest
from sqlalchemy import (
    INTEGER,
    VARCHAR,
    TEXT,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import ENUM

from schema_alchemist.generators import TableGenerator


def test_create_foreign_key_constraint(pre_configured_ipr):
    expected = (
        "ForeignKeyConstraint(columns=['user_id'], refcolumns=["
        "'public.users.id'], name='fk_user', ondelete='CASCADE')"
    )
    reflected_data = {
        "name": "fk_user",
        "constrained_columns": ["user_id"],
        "referred_schema": "public",
        "referred_table": "users",
        "referred_columns": ["id"],
        "options": {"ondelete": "CASCADE"},
        "comment": None,
    }
    generator = TableGenerator(
        "test",
        "metadata",
        pre_configured_ipr,
        schema="public",
        foreign_keys=[reflected_data],
    )

    assert generator.create_fk_constraint(reflected_data) == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {
                "name": "category_name_idx",
                "unique": False,
                "column_names": ["name"],
                "include_columns": [],
                "dialect_options": {"postgresql_include": []},
            },
            "Index('category_name_idx', 'name')",
        ),
        (
            {
                "name": "categories_name_key",
                "unique": True,
                "column_names": ["name"],
                "duplicates_constraint": "categories_name_key",
                "include_columns": [],
                "dialect_options": {"postgresql_include": []},
            },
            "Index('categories_name_key', 'name', unique=True)",
        ),
    ],
)
def test_create_index_constraint(data, expected, pre_configured_ipr):
    generator = TableGenerator("test", "metadata", pre_configured_ipr, indexes=[data])

    assert generator.create_index_constraint(data) == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {
                "constrained_columns": ["product_id", "category_id"],
                "name": "product_categories_pkey",
                "comment": None,
            },
            "PrimaryKeyConstraint('product_id', 'category_id', name='product_categories_pkey')",
        ),
        (
            {"constrained_columns": ["id"], "name": "orders_pkey", "comment": None},
            "PrimaryKeyConstraint('id', name='orders_pkey')",
        ),
    ],
)
def test_create_primary_key_constraint(data, expected, pre_configured_ipr):
    generator = TableGenerator("test", "metadata", pre_configured_ipr, primary_key=data)
    assert generator.create_pk_constraint(data) == expected


def test_create_unique_constraint(pre_configured_ipr):
    data = {"column_names": ["name"], "name": "categories_name_key", "comment": None}
    expected = "UniqueConstraint('name', name='categories_name_key')"

    generator = TableGenerator(
        "test", "metadata", pre_configured_ipr, unique_constraints=[data]
    )

    assert generator.create_unique_constraint(data) == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {
                "name": "order_items_quantity_check",
                "sqltext": "quantity > 0",
                "comment": None,
            },
            "CheckConstraint(sqltext='quantity > 0', name='order_items_quantity_check')",
        ),
        (
            {
                "name": "order_items_unit_price_check",
                "sqltext": "unit_price >= 0::numeric",
                "comment": None,
            },
            "CheckConstraint(sqltext='unit_price >= 0::numeric', name='order_items_unit_price_check')",
        ),
    ],
)
def test_create_check_constraints(data, expected, pre_configured_ipr):

    generator = TableGenerator(
        "test", "metadata", pre_configured_ipr, check_constraints=[data]
    )

    assert generator.create_check_constraint(data) == expected


@patch.object(TableGenerator, "create_unique_constraint")
@patch.object(TableGenerator, "create_pk_constraint")
@patch.object(TableGenerator, "create_fk_constraint")
@patch.object(TableGenerator, "create_check_constraint")
@patch.object(TableGenerator, "create_index_constraint")
def test_create_constraints(
    create_index_constraint_mock,
    create_check_constraint_mock,
    create_fk_constraint_mock,
    create_pk_constraint,
    create_unique_constraint_mock,
    pre_configured_ipr,
):
    index_mock = create_index_constraint_mock.return_value
    check_mock = create_check_constraint_mock.return_value
    fk_mock = create_fk_constraint_mock.return_value
    pk_mock = create_pk_constraint.return_value
    unique_mock = create_unique_constraint_mock.return_value

    generator = TableGenerator(
        "test",
        "metadata",
        pre_configured_ipr,
        check_constraints=[{}],
        foreign_keys=[{}],
        indexes=[{}, {"duplicates_constraint": "test"}],
        primary_key={"test": 1},
        unique_constraints=[{}],
    )

    constraints = generator.create_constraints()
    assert constraints == [pk_mock, fk_mock, index_mock, unique_mock, check_mock]

    create_index_constraint_mock.assert_called_once_with({})
    create_check_constraint_mock.assert_called_once_with({})
    create_fk_constraint_mock.assert_called_once_with({})
    create_pk_constraint.assert_called_once_with({"test": 1})
    create_unique_constraint_mock.assert_called_once_with({})


UserTable = """Users = Table('users', metadata,
    Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".users_id_seq\\'::regclass)'),
    Column('first_name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('last_name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('full_name', VARCHAR(length=201), Computed(sqltext="(((first_name)::text || ' '::text) || (last_name)::text)", persisted=True), autoincrement=False, nullable=True),
    Column('email', VARCHAR(length=255), autoincrement=False, unique=True, nullable=False),
    Column('role', ENUM('admin', 'user', 'guest', name='user_role'), autoincrement=False, nullable=False, server_default="'user'::user_role"),
    Column('phone_numbers', ARRAY(TEXT()), autoincrement=False, nullable=True),

    PrimaryKeyConstraint('id', name='users_pkey'),
    UniqueConstraint('email', name='users_email_key'),
    schema = 'public'
)"""


@pytest.mark.parametrize(
    "name, schema, columns, comment, check_constraints, foreign_keys, indexes, "
    "primary_key, unique_constraints, expected",
    (
        (
            "users",
            "public",
            # columns
            [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": "nextval('\"public\".users_id_seq'::regclass)",
                    "autoincrement": True,
                    "comment": None,
                },
                {
                    "name": "first_name",
                    "type": VARCHAR(length=100),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "last_name",
                    "type": VARCHAR(length=100),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "full_name",
                    "type": VARCHAR(length=201),
                    "nullable": True,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                    "computed": {
                        "sqltext": "(((first_name)::text || ' '::text) || (last_name)::text)",
                        "persisted": True,
                    },
                },
                {
                    "name": "email",
                    "type": VARCHAR(length=255),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "role",
                    "type": ENUM("admin", "user", "guest", name="user_role"),
                    "nullable": False,
                    "default": "'user'::user_role",
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "phone_numbers",
                    "type": ARRAY(TEXT()),
                    "nullable": True,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            # comment
            {"text": None},
            # check constraints
            [],
            # foreign keys
            [],
            # indexes
            [
                {
                    "name": "users_email_key",
                    "unique": True,
                    "column_names": ["email"],
                    "duplicates_constraint": "users_email_key",
                    "include_columns": [],
                    "dialect_options": {"postgresql_include": []},
                }
            ],
            # primary key
            {"constrained_columns": ["id"], "name": "users_pkey", "comment": None},
            # unique constraints
            [{"column_names": ["email"], "name": "users_email_key", "comment": None}],
            # expected output
            UserTable,
        ),
    ),
)
def test_table_generator(
    pre_configured_ipr,
    name,
    schema,
    columns,
    comment,
    check_constraints,
    foreign_keys,
    indexes,
    primary_key,
    unique_constraints,
    expected,
):
    generator = TableGenerator(
        name,
        "metadata",
        import_path_resolver=pre_configured_ipr,
        schema=schema,
        columns=columns,
        comment=comment,
        check_constraints=check_constraints,
        foreign_keys=foreign_keys,
        indexes=indexes,
        primary_key=primary_key,
        unique_constraints=unique_constraints,
    )
    assert generator.generate() == expected
