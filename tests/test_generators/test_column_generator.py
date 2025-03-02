from datetime import datetime, date
from decimal import Decimal

import pytest
from sqlalchemy import (
    Integer,
    VARCHAR,
    NUMERIC,
    DOUBLE_PRECISION,
    DATE,
    INTEGER,
    TEXT,
    TIMESTAMP,
)
from sqlalchemy.dialects.mysql import ENUM

from schema_alchemist.generators import ColumnGenerator
from schema_alchemist.utils import StringReprWrapper


def test_create_fk_constraint(pre_configured_ipr):
    fk_data = {
        "name": "orders_user_id_fkey",
        "constrained_columns": ["user_id"],
        "referred_schema": "public",
        "referred_table": "users",
        "referred_columns": ["id"],
        "options": {"ondelete": "CASCADE"},
        "comment": None,
    }

    expected = StringReprWrapper(
        "ForeignKey(column='users.id', name='orders_user_id_fkey', ondelete='CASCADE')"
    )

    column_data = {
        "type": Integer(),
        "name": "id",
        "nullable": False,
        "foreign_key": fk_data,
    }
    column_generator = ColumnGenerator(column_data, pre_configured_ipr, "TestTable")
    result = column_generator.create_fk_constraint()
    assert result == expected


@pytest.mark.parametrize(
    "input_value, expected",
    (
        (
            {
                "sqltext": "((quantity)::numeric * unit_price)",
                "persisted": True,
            },
            "Computed(sqltext='((quantity)::numeric * unit_price)', persisted=True)",
        ),
        (
            {
                "sqltext": "((quantity)::numeric * unit_price)",
                "persisted": False,
            },
            "Computed(sqltext='((quantity)::numeric * unit_price)', persisted=False)",
        ),
    ),
)
def test_create_column_computed(pre_configured_ipr, input_value, expected):
    column_data = {
        "name": "total_price",
        "type": NUMERIC(precision=10, scale=2),
        "nullable": True,
        "default": None,
        "autoincrement": False,
        "comment": None,
        "computed": input_value,
    }
    expected = StringReprWrapper(expected)
    column_generator = ColumnGenerator(column_data, pre_configured_ipr, "TestTable")
    result = column_generator.create_column_computed()
    assert result == expected


def test_create_column_computed_none(import_path_resolver):
    column_data = {
        "name": "total_price",
        "type": NUMERIC(precision=10, scale=2),
        "nullable": True,
        "default": None,
        "autoincrement": False,
        "comment": None,
    }

    column_generator = ColumnGenerator(column_data, import_path_resolver, "TestTable")
    result = column_generator.create_column_computed()
    assert result is None


@pytest.mark.parametrize(
    "input_value, expected",
    (
        (
            {
                "name": "id",
                "type": INTEGER(),
                "nullable": False,
                "default": "nextval('\"public\".addresses_id_seq'::regclass)",
                "autoincrement": True,
                "comment": None,
            },
            "    Column('id', INTEGER(), autoincrement=True, nullable=False, "
            "server_default='nextval(\\'\"public\".addresses_id_seq\\'::regclass)')",
        ),
        (
            {
                "name": "user_id",
                "type": INTEGER(),
                "nullable": False,
                "default": None,
                "autoincrement": False,
                "comment": None,
            },
            "    Column('user_id', INTEGER(), autoincrement=False, nullable=False)",
        ),
        (
            {
                "name": "address_line1",
                "type": VARCHAR(length=200),
                "nullable": False,
                "default": None,
                "autoincrement": False,
                "comment": None,
            },
            "    Column('address_line1', VARCHAR(length=200), "
            "autoincrement=False, nullable=False)",
        ),
        (
            {
                "name": "created_at",
                "type": TIMESTAMP(),
                "nullable": False,
                "default": "CURRENT_TIMESTAMP",
                "autoincrement": False,
                "comment": None,
            },
            "    Column('created_at', TIMESTAMP(), autoincrement=False, nullable=False, "
            "server_default='CURRENT_TIMESTAMP')",
        ),
        (
            {
                "name": "description",
                "type": TEXT(),
                "nullable": True,
                "default": None,
                "autoincrement": False,
                "comment": None,
            },
            "    Column('description', TEXT(), autoincrement=False, nullable=True)",
        ),
        (
            {
                "name": "order_date",
                "type": DATE(),
                "nullable": True,
                "default": "CURRENT_DATE",
                "autoincrement": False,
                "comment": None,
            },
            "    Column('order_date', DATE(), autoincrement=False, nullable=True, "
            "server_default='CURRENT_DATE')",
        ),
        (
            {
                "name": "status",
                "type": ENUM(
                    "pending",
                    "processed",
                    "shipped",
                    "delivered",
                    "cancelled",
                    name="order_status_enum",
                ),
                "nullable": False,
                "default": "'pending'::order_status_enum",
                "autoincrement": False,
                "comment": None,
            },
            "    Column('status', ENUM('pending', 'processed', 'shipped', 'delivered', "
            "'cancelled'), autoincrement=False, nullable=False, "
            "server_default=\"'pending'::order_status_enum\")",
        ),
        (
            {
                "name": "total_amount",
                "type": NUMERIC(precision=10, scale=2),
                "nullable": False,
                "default": None,
                "autoincrement": False,
                "comment": None,
            },
            "    Column('total_amount', NUMERIC(precision=10, scale=2), "
            "autoincrement=False, nullable=False)",
        ),
        (
            {
                "name": "unit_price",
                "type": DOUBLE_PRECISION(precision=53),
                "nullable": False,
                "default": None,
                "autoincrement": False,
                "comment": None,
            },
            "    Column('unit_price', DOUBLE_PRECISION(precision=53), "
            "autoincrement=False, nullable=False)",
        ),
        (
            {
                "name": "total_price",
                "type": NUMERIC(precision=10, scale=2),
                "nullable": True,
                "default": None,
                "autoincrement": False,
                "comment": None,
                "computed": {
                    "sqltext": "((quantity)::numeric * unit_price)",
                    "persisted": True,
                },
            },
            "    Column('total_price', NUMERIC(precision=10, scale=2), "
            "Computed(sqltext='((quantity)::numeric * unit_price)', persisted=True), "
            "autoincrement=False, nullable=True)",
        ),
        (
            {
                "name": "id",
                "type": INTEGER(),
                "nullable": False,
                "default": None,
                "autoincrement": True,
                "comment": None,
                "identity": {
                    "always": False,
                    "start": 1,
                    "increment": 1,
                    "minvalue": 1,
                    "maxvalue": 2147483647,
                    "cache": 1,
                    "cycle": False,
                },
            },
            "    Column('id', INTEGER(), "
            "Identity(start=1, increment=1, minvalue=1, maxvalue=2147483647, "
            "cycle=False, cache=1), "
            "autoincrement=True, nullable=False)",
        ),
    ),
)
def test_core_column_generate(pre_configured_ipr, input_value, expected):
    column_generator = ColumnGenerator(input_value, pre_configured_ipr, "TestTable")
    result = column_generator.generate()
    assert result == expected


@pytest.mark.parametrize(
    "input_value, expected",
    (
        (
            {
                "name": "id",
                "type": INTEGER(),
                "nullable": False,
            },
            {
                "column_name": "id",
                "column_type": "INTEGER()",
                "column_nullable": False,
                "column_type_class": INTEGER,
                "column_python_type": int,
            },
        ),
        (
            {
                "name": "address",
                "type": VARCHAR(length=200),
                "nullable": False,
            },
            {
                "column_name": "address",
                "column_type": "VARCHAR(length=200)",
                "column_nullable": False,
                "column_type_class": VARCHAR,
                "column_python_type": str,
            },
        ),
        (
            {
                "name": "created_at",
                "type": TIMESTAMP(),
                "nullable": False,
            },
            {
                "column_name": "created_at",
                "column_type": "TIMESTAMP()",
                "column_nullable": False,
                "column_type_class": TIMESTAMP,
                "column_python_type": datetime,
            },
        ),
        (
            {
                "name": "description",
                "type": TEXT(),
                "nullable": True,
            },
            {
                "column_name": "description",
                "column_type": "TEXT()",
                "column_nullable": True,
                "column_type_class": TEXT,
                "column_python_type": str,
            },
        ),
        (
            {
                "name": "order_date",
                "type": DATE(),
                "nullable": True,
            },
            {
                "column_name": "order_date",
                "column_type": "DATE()",
                "column_nullable": True,
                "column_type_class": DATE,
                "column_python_type": date,
            },
        ),
        (
            {
                "name": "total_amount",
                "type": NUMERIC(precision=10, scale=2),
                "nullable": False,
            },
            {
                "column_name": "total_amount",
                "column_type": "NUMERIC(precision=10, scale=2)",
                "column_nullable": False,
                "column_type_class": NUMERIC,
                "column_python_type": Decimal,
            },
        ),
        (
            {
                "name": "unit_price",
                "type": DOUBLE_PRECISION(precision=53),
                "nullable": False,
            },
            {
                "column_name": "unit_price",
                "column_type": "DOUBLE_PRECISION(precision=53)",
                "column_nullable": False,
                "column_type_class": DOUBLE_PRECISION,
                "column_python_type": float,
            },
        ),
    ),
)
def test_properties(pre_configured_ipr, input_value, expected):
    cg = ColumnGenerator(input_value, pre_configured_ipr, "TestTable")
    assert cg.column_name == expected["column_name"]
    assert cg.column_type.__repr__() == expected["column_type"]
    assert cg.column_nullable == expected["column_nullable"]
    assert cg.column_type_class == expected["column_type_class"]
    assert cg.column_python_type == expected["column_python_type"]


def test_column_enum_type(import_path_resolver):
    data = {
        "name": "status",
        "type": ENUM(
            "pending",
            "processed",
            "shipped",
            "delivered",
            "cancelled",
            name="order_status_enum",
        ),
        "nullable": False,
    }

    cg = ColumnGenerator(data, import_path_resolver, "TestTable")

    assert cg.column_python_type == "order_status_enum"

    assert cg.column_name == "status"
    assert (
        cg.column_type.__repr__()
        == "ENUM('pending', 'processed', 'shipped', 'delivered', 'cancelled')"
    )
    assert not cg.column_nullable
    assert cg.column_type_class == ENUM
