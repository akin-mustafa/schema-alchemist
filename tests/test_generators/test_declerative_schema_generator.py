from unittest.mock import patch

import pytest
from sqlalchemy import Column, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase

from schema_alchemist.constants import SQLRelationshipType
from schema_alchemist.generators import DeclarativeSchemaGenerator
from schema_alchemist.utils import make_in_file_obj, StringReprWrapper


def test_metadata_name(reflected_data, sorted_tables):
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables)

    assert sg.metadata_name == "Base"


def test_schema_type_imports(reflected_data, sorted_tables):
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables)

    assert sg.schema_type_imports == (
        DeclarativeBase,
        Mapped,
        mapped_column,
        relationship,
        Column,
        Table,
    )


def test_generate_base_definition(reflected_data, sorted_tables):
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables, schema="public")
    sg.collect_imports()
    expected = "class Base(DeclarativeBase):\n    pass"
    assert sg.generate_base_definition() == expected

    sg.import_path_resolver.insert(make_in_file_obj("DeclarativeBase"))
    sg.table_class_name_map[(None, "base")] = "Base"

    expected = "class Base_(decl_api_DeclarativeBase):\n    pass"
    assert sg.generate_base_definition() == expected


def test_get_suffixes_snake_case(reflected_data, sorted_tables):
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables)
    assert sg.get_suffixes() == ["_detail", "_instance", "_data"]
    assert sg.get_suffixes(True) == ["_detail", "_instance", "_data"]
    assert sg.get_suffixes(False) == ["_set", "_list", "_data"]


def test_get_suffixes_camel_case(reflected_data, sorted_tables):
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables, use_camel_case=True)
    assert sg.get_suffixes() == ["Detail", "Instance", "Data"]
    assert sg.get_suffixes(True) == ["Detail", "Instance", "Data"]
    assert sg.get_suffixes(False) == ["Set", "List", "Data"]


@pytest.mark.parametrize(
    "attr_name, main_tabel, target_table, use_singular_suffixes, expected",
    (
        ("user_id", ("public", "orders"), ("public", "users"), True, "user_id_detail"),
        ("user_id", ("public", "orders"), ("public", "users"), False, "user_id_set"),
        ("users", ("public", "orders"), ("public", "users"), True, "users"),
        ("users", ("public", "orders"), ("public", "users"), False, "users"),
    ),
)
def test_find_unique_key_for_relation_attribute(
    attr_name,
    main_tabel,
    target_table,
    use_singular_suffixes,
    expected,
    reflected_data,
    sorted_tables,
):
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables)
    result = sg.find_unique_key_for_relation_attribute(
        attr_name, main_tabel, target_table, use_singular_suffixes
    )
    assert result == expected


@patch.object(DeclarativeSchemaGenerator, "get_suffixes", return_value=[])
def test_find_unique_key_for_relation_attribute_fails(
    mock_get_suffixes,
    reflected_data,
    sorted_tables,
):
    expected = (
        r"No suitable relationship attribute name found for users in Table: orders"
    )
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables)

    with pytest.raises(ValueError, match=expected):
        sg.find_unique_key_for_relation_attribute(
            "user_id",
            ("public", "orders"),
            ("public", "users"),
            True,
        )


@pytest.mark.parametrize(
    "table, expected",
    (
        (("public", "students"), (False, False)),  # no fk
        (("public", "order_items"), (False, False)),  # not m2m
        (("public", "order_items"), (False, False)),  # not m2m
        # m2m without pk
        (("public", "product_categories"), (True, False)),
        # ternary m2m with pk
        (("public", "student_course_instructors"), (True, False)),
        # self referencing m2m with pk
        (
            ("public", "employee_relationships"),
            (True, True),
        ),
    ),
)
def test_resolve_m2m_relationship(table, expected, reflected_data, sorted_tables):
    sg = DeclarativeSchemaGenerator(
        reflected_data,
        sorted_tables,
    )
    assert sg.resolve_m2m_relationship(table) == expected


@pytest.mark.parametrize(
    "main_tabel, target_table, relationship_type, constrained_columns, expected_name",
    (
        (
            ("public", "categories"),
            ("public", "categories"),
            SQLRelationshipType.o2m,
            ["parent_id"],
            "parent",
        ),
        (
            ("public", "employees"),
            ("public", "employees"),
            SQLRelationshipType.m2m,
            ["employee_id"],
            "employees",
        ),
        (
            ("public", "employees"),
            ("public", "employees"),
            SQLRelationshipType.m2m,
            ["related_employee_id"],
            "related_employees",
        ),
        (
            ("public", "categories"),
            ("public", "products"),
            SQLRelationshipType.m2m,
            ["category_id"],
            "categories",
        ),
        (
            ("public", "products"),
            ("public", "categories"),
            SQLRelationshipType.m2m,
            ["product_id"],
            "products",
        ),
        (
            ("public", "profiles"),
            ("public", "users"),
            SQLRelationshipType.o2o,
            ["user_id"],
            "user",
        ),
    ),
)
def test_convert_to_relation_attribute_name(
    reflected_data,
    sorted_tables,
    main_tabel,
    target_table,
    relationship_type,
    constrained_columns,
    expected_name,
):
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables, "public")
    attr_name = sg.create_to_relation_attribute_name(
        main_tabel, target_table, relationship_type, constrained_columns
    )

    assert attr_name == expected_name


@pytest.mark.parametrize(
    "table, fk, expected",
    (
        (
            ("public", "profiles"),
            {
                "name": "fk_user",
                "constrained_columns": ["user_id"],
                "referred_schema": "public",
                "referred_table": "users",
                "referred_columns": ["id"],
                "options": {"ondelete": "CASCADE"},
                "comment": None,
            },
            SQLRelationshipType.o2o,
        ),
        (
            ("public", "orders"),
            {
                "name": "fk_user_order",
                "constrained_columns": ["user_id"],
                "referred_schema": "public",
                "referred_table": "users",
                "referred_columns": ["id"],
                "options": {"ondelete": "CASCADE"},
                "comment": None,
            },
            SQLRelationshipType.o2m,
        ),
    ),
)
def test_resolve_relationship_type_of_fk(
    table, fk, expected, reflected_data, sorted_tables
):
    sg = DeclarativeSchemaGenerator(
        reflected_data,
        sorted_tables,
    )
    assert sg.resolve_relationship_type_of_fk(table, fk) == expected


def test_resolve_relationships(reflected_data, sorted_tables):
    expected = {
        ("public", "categories"): [
            {
                "attribute_name": "parent",
                "target_class": "Categories",
                "back_populates": "sub_categories",
                "relation_type": SQLRelationshipType.o2m,
                "nullable": False,
                "secondary_table": None,
                "remote_side": "Categories.id",
                "foreign_keys": "[Categories.parent_id,]",
            },
            {
                "attribute_name": "sub_categories",
                "target_class": "Categories",
                "back_populates": "parent",
                "relation_type": SQLRelationshipType.m2o,
                "nullable": False,
                "secondary_table": None,
                "foreign_keys": "[Categories.parent_id,]",
            },
            {
                "attribute_name": "products",
                "target_class": "Products",
                "back_populates": "categories",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "ProductCategories",
            },
        ],
        ("public", "employees"): [
            {
                "attribute_name": "related_employees",
                "target_class": "Employees",
                "back_populates": "employees",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "EmployeeRelationships",
                "primaryjoin": StringReprWrapper(
                    "id == EmployeeRelationships.c.employee_id"
                ),
                "secondaryjoin": StringReprWrapper(
                    "id == EmployeeRelationships.c.related_employee_id"
                ),
            },
            {
                "attribute_name": "employees",
                "target_class": "Employees",
                "back_populates": "related_employees",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "EmployeeRelationships",
                "primaryjoin": StringReprWrapper(
                    "id == EmployeeRelationships.c.related_employee_id"
                ),
                "secondaryjoin": StringReprWrapper(
                    "id == EmployeeRelationships.c.employee_id"
                ),
            },
        ],
        ("public", "order_items"): [
            {
                "attribute_name": "order",
                "target_class": "Orders",
                "back_populates": "order_items",
                "relation_type": SQLRelationshipType.o2m,
                "nullable": False,
                "secondary_table": None,
                "foreign_keys": "[OrderItems.order_id,]",
            },
            {
                "attribute_name": "product",
                "target_class": "Products",
                "back_populates": "order_items",
                "relation_type": SQLRelationshipType.o2m,
                "nullable": False,
                "secondary_table": None,
                "foreign_keys": "[OrderItems.product_id,]",
            },
        ],
        ("public", "orders"): [
            {
                "attribute_name": "order_items",
                "target_class": "OrderItems",
                "back_populates": "order",
                "relation_type": SQLRelationshipType.m2o,
                "nullable": False,
                "secondary_table": None,
                "foreign_keys": "[OrderItems.order_id,]",
            },
            {
                "attribute_name": "user",
                "target_class": "Users",
                "back_populates": "orders",
                "relation_type": SQLRelationshipType.o2m,
                "nullable": False,
                "secondary_table": None,
                "foreign_keys": "[Orders.user_id,]",
            },
        ],
        ("public", "products"): [
            {
                "attribute_name": "order_items",
                "target_class": "OrderItems",
                "back_populates": "product",
                "relation_type": SQLRelationshipType.m2o,
                "nullable": False,
                "secondary_table": None,
                "foreign_keys": "[OrderItems.product_id,]",
            },
            {
                "attribute_name": "categories",
                "target_class": "Categories",
                "back_populates": "products",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "ProductCategories",
            },
        ],
        ("public", "users"): [
            {
                "attribute_name": "orders",
                "target_class": "Orders",
                "back_populates": "user",
                "relation_type": SQLRelationshipType.m2o,
                "nullable": False,
                "secondary_table": None,
                "foreign_keys": "[Orders.user_id,]",
            },
            {
                "attribute_name": "profile",
                "target_class": "Profiles",
                "back_populates": "user",
                "relation_type": SQLRelationshipType.o2o,
                "nullable": False,
                "secondary_table": None,
                "foreign_keys": "[Profiles.user_id,]",
            },
        ],
        ("public", "profiles"): [
            {
                "attribute_name": "user",
                "target_class": "Users",
                "back_populates": "profile",
                "relation_type": SQLRelationshipType.o2o,
                "nullable": False,
                "secondary_table": None,
                "foreign_keys": "[Profiles.user_id,]",
            }
        ],
    }

    sg = DeclarativeSchemaGenerator(
        reflected_data,
        sorted_tables,
        schema="public",
    )
    sg.resolve_relationships()
    assert dict(sg.relationships) == expected


def test_generate_enum(reflected_data, sorted_tables):
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables, schema="public")

    sg.collect_imports()

    assert sg.generate_enums() == [
        (
            "class order_status(enum_Enum):\n"
            "    pending = 'pending'\n"
            "    paid = 'paid'\n"
            "    cancelled = 'cancelled'\n"
            "    shipped = 'shipped'"
        ),
        (
            "class user_role(enum_Enum):\n"
            "    admin = 'admin'\n"
            "    user = 'user'\n"
            "    guest = 'guest'"
        ),
    ]


def test_declarative_schema_generate(reflected_data, sorted_tables, declarative_table):
    sg = DeclarativeSchemaGenerator(reflected_data, sorted_tables, schema="public")

    assert sg.generate() == declarative_table
