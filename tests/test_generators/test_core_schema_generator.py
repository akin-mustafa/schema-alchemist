from sqlalchemy import Column, Table, MetaData

from schema_alchemist.generators import CoreSchemaGenerator
from schema_alchemist.utils import make_in_file_obj


def test_sorted_table(reflected_data, sorted_tables):
    expected = [
        ("public", "categories"),
        ("public", "courses"),
        ("public", "employees"),
        ("public", "instructors"),
        ("public", "products"),
        ("public", "students"),
        ("public", "users"),
        ("public", "employee_relationships"),
        ("public", "orders"),
        ("public", "product_categories"),
        ("public", "profiles"),
        ("public", "student_course_instructors"),
        ("public", "order_items"),
    ]
    sg = CoreSchemaGenerator(reflected_data, sorted_tables, schema="public")

    assert sg.sorted_tables == expected


def test_metadata_name(reflected_data, sorted_tables):
    sg = CoreSchemaGenerator(reflected_data, sorted_tables, schema="public")

    assert sg.metadata_name == "metadata"


def test_find_unique_name(reflected_data, sorted_tables):
    sg = CoreSchemaGenerator(reflected_data, sorted_tables, schema="public")
    sg.table_class_name_map = {"test": "metadata"}

    assert sg.find_unique_name("metadata") == "metadata_"


def test_schema_type_imports(reflected_data, sorted_tables):
    sg = CoreSchemaGenerator(reflected_data, sorted_tables, schema="public")
    assert sg.schema_type_imports == (Table, Column, MetaData)


def test_generate_base_definition(reflected_data, sorted_tables):
    sg = CoreSchemaGenerator(reflected_data, sorted_tables, schema="public")
    sg.collect_imports()

    assert sg.generate_base_definition() == "metadata = MetaData(schema='public')"

    sg.import_path_resolver.insert(make_in_file_obj("MetaData"))

    assert (
        sg.generate_base_definition() == "metadata = schema_MetaData(schema='public')"
    )


def test_generate_imports(reflected_data, sorted_tables):
    expected = """from datetime import datetime
from decimal import Decimal
from enum import Enum as enum_Enum
from sqlalchemy.sql.schema import (
    CheckConstraint,
    Column,
    Computed,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    MetaData,
    PrimaryKeyConstraint,
    Table,
    UniqueConstraint
)
from sqlalchemy.sql.sqltypes import (
    ARRAY,
    Enum as sqltypes_Enum,
    INTEGER,
    NUMERIC,
    TEXT,
    TIMESTAMP,
    VARCHAR
)
from typing import (
    List,
    Optional
)"""
    sg = CoreSchemaGenerator(reflected_data, sorted_tables, schema="public")
    sg.collect_imports()
    assert sg.generate_imports() == expected


def test_core_schema_generate(reflected_data, sorted_tables, core_table):

    sg = CoreSchemaGenerator(reflected_data, sorted_tables, schema="public")

    assert sg.generate() == core_table
