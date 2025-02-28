from unittest.mock import patch

import pytest
from sqlalchemy import Column
from sqlmodel import Relationship, Field, SQLModel

from schema_alchemist.constants import SQLRelationshipType
from schema_alchemist.generators import SQLModelSchemaGenerator


def test_metadata_name(reflected_data, sorted_tables):
    sg = SQLModelSchemaGenerator(reflected_data, sorted_tables)

    assert sg.metadata_name == "Base"


def test_schema_type_imports(reflected_data, sorted_tables):
    sg = SQLModelSchemaGenerator(reflected_data, sorted_tables)

    assert sg.schema_type_imports == (SQLModel, Field, Relationship, Column)


def test_generate_base_definition(reflected_data, sorted_tables):
    sg = SQLModelSchemaGenerator(reflected_data, sorted_tables, schema="public")
    sg.collect_imports()
    assert sg.generate_base_definition() == ""


def test_get_suffixes_snake_case(reflected_data, sorted_tables):
    sg = SQLModelSchemaGenerator(reflected_data, sorted_tables)
    assert sg.get_suffixes() == ["_detail", "_instance", "_data"]
    assert sg.get_suffixes(True) == ["_detail", "_instance", "_data"]
    assert sg.get_suffixes(False) == ["_set", "_list", "_data"]


def test_get_suffixes_camel_case(reflected_data, sorted_tables):
    sg = SQLModelSchemaGenerator(reflected_data, sorted_tables, use_camel_case=True)
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
    sg = SQLModelSchemaGenerator(reflected_data, sorted_tables)
    result = sg.find_unique_key_for_relation_attribute(
        attr_name, main_tabel, target_table, use_singular_suffixes
    )
    assert result == expected


@pytest.mark.parametrize(
    "main_tabel, target_table, relationship_type, expected_attr_name, expected_back_population",
    (
        (
            ("public", "orders"),
            ("public", "users"),
            SQLRelationshipType.o2m,
            "user",
            "orders",
        ),
        (
            ("public", "profiles"),
            ("public", "users"),
            SQLRelationshipType.o2o,
            "user",
            "profile",
        ),
        (
            ("public", "students"),
            ("public", "instructors"),
            SQLRelationshipType.m2m,
            "instructors",
            "students",
        ),
        (
            ("public", "categories"),
            ("public", "products"),
            SQLRelationshipType.m2m,
            "products",
            "categories",
        ),
    ),
)
def test_resolve_relation_and_back_populates_names(
    main_tabel,
    target_table,
    relationship_type,
    expected_attr_name,
    expected_back_population,
    relationship_reflected_data,
    relationship_sorted_tables,
):
    sg = SQLModelSchemaGenerator(
        relationship_reflected_data,
        relationship_sorted_tables,
        schema="public",
    )
    attr_name, back_population = sg.resolve_relation_and_back_populates_names(
        main_tabel, target_table, relationship_type
    )

    assert attr_name == expected_attr_name
    assert back_population == expected_back_population


@patch.object(SQLModelSchemaGenerator, "get_suffixes", return_value=[])
def test_find_unique_key_for_relation_attribute_fails(
    mock_get_suffixes,
    reflected_data,
    sorted_tables,
):
    expected = (
        r"No suitable relationship attribute name found for users in Table: orders"
    )
    sg = SQLModelSchemaGenerator(reflected_data, sorted_tables)

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
        (("public", "students"), None),  # no fk
        (("public", "order_items"), None),  # not m2m
        (("public", "order_items"), None),  # not m2m
        (
            ("public", "product_categories"),
            {("public", "products"), ("public", "categories")},
        ),  # m2m without pk
        (
            ("public", "student_course_instructors"),
            {("public", "students"), ("public", "instructors"), ("public", "courses")},
        ),  # ternary m2m with pk
    ),
)
def test_resolve_m2m_relationship(
    table, expected, relationship_reflected_data, relationship_sorted_tables
):
    fks = relationship_reflected_data.foreign_keys[table]
    sg = SQLModelSchemaGenerator(
        relationship_reflected_data,
        relationship_sorted_tables,
    )
    assert sg.resolve_m2m_relationship(table, fks) == expected


@pytest.mark.parametrize(
    "table, fk, expected",
    (
        (
            ("public", "email_addresses"),
            {
                "name": "fk_user_email_address",
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
    table, fk, expected, relationship_reflected_data, relationship_sorted_tables
):
    sg = SQLModelSchemaGenerator(
        relationship_reflected_data,
        relationship_sorted_tables,
    )
    assert sg.resolve_relationship_type_of_fk(table, fk) == expected


def test_resolve_relationships(relationship_reflected_data, relationship_sorted_tables):
    expected = {
        ("public", "order_items"): [
            {
                "attribute_name": "order",
                "target_class": "Order",
                "back_populates": "order_items",
                "relation_type": SQLRelationshipType.o2m,
                "nullable": False,
                "secondary_table": None,
            },
            {
                "attribute_name": "product",
                "target_class": "Product",
                "back_populates": "order_items",
                "relation_type": SQLRelationshipType.o2m,
                "nullable": False,
                "secondary_table": None,
            },
        ],
        ("public", "orders"): [
            {
                "attribute_name": "order_items",
                "target_class": "OrderItem",
                "back_populates": "order",
                "relation_type": SQLRelationshipType.m2o,
                "nullable": False,
                "secondary_table": None,
            },
            {
                "attribute_name": "user",
                "target_class": "User",
                "back_populates": "orders",
                "relation_type": SQLRelationshipType.o2m,
                "nullable": False,
                "secondary_table": None,
            },
        ],
        ("public", "products"): [
            {
                "attribute_name": "order_items",
                "target_class": "OrderItem",
                "back_populates": "product",
                "relation_type": SQLRelationshipType.m2o,
                "nullable": False,
                "secondary_table": None,
            },
            {
                "attribute_name": "categories",
                "target_class": "Category",
                "back_populates": "products",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "ProductCategory",
            },
        ],
        ("public", "users"): [
            {
                "attribute_name": "orders",
                "target_class": "Order",
                "back_populates": "user",
                "relation_type": SQLRelationshipType.m2o,
                "nullable": False,
                "secondary_table": None,
            },
            {
                "attribute_name": "email_address",
                "target_class": "EmailAddress",
                "back_populates": "user",
                "relation_type": SQLRelationshipType.o2o,
                "nullable": False,
                "secondary_table": None,
            },
            {
                "attribute_name": "profile",
                "target_class": "Profile",
                "back_populates": "user",
                "relation_type": SQLRelationshipType.o2o,
                "nullable": False,
                "secondary_table": None,
            },
        ],
        ("public", "email_addresses"): [
            {
                "attribute_name": "user",
                "target_class": "User",
                "back_populates": "email_address",
                "relation_type": SQLRelationshipType.o2o,
                "nullable": False,
                "secondary_table": None,
            }
        ],
        ("public", "courses"): [
            {
                "attribute_name": "instructors",
                "target_class": "Instructor",
                "back_populates": "courses",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "StudentCourseInstructor",
            },
            {
                "attribute_name": "students",
                "target_class": "Student",
                "back_populates": "courses",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "StudentCourseInstructor",
            },
        ],
        ("public", "instructors"): [
            {
                "attribute_name": "courses",
                "target_class": "Course",
                "back_populates": "instructors",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "StudentCourseInstructor",
            },
            {
                "attribute_name": "students",
                "target_class": "Student",
                "back_populates": "instructors",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "StudentCourseInstructor",
            },
        ],
        ("public", "students"): [
            {
                "attribute_name": "courses",
                "target_class": "Course",
                "back_populates": "students",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "StudentCourseInstructor",
            },
            {
                "attribute_name": "instructors",
                "target_class": "Instructor",
                "back_populates": "students",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "StudentCourseInstructor",
            },
        ],
        ("public", "categories"): [
            {
                "attribute_name": "products",
                "target_class": "Product",
                "back_populates": "categories",
                "relation_type": SQLRelationshipType.m2m,
                "nullable": False,
                "secondary_table": "ProductCategory",
            }
        ],
        ("public", "profiles"): [
            {
                "attribute_name": "user",
                "target_class": "User",
                "back_populates": "profile",
                "relation_type": SQLRelationshipType.o2o,
                "nullable": False,
                "secondary_table": None,
            }
        ],
    }
    sg = SQLModelSchemaGenerator(
        relationship_reflected_data,
        relationship_sorted_tables,
        schema="public",
    )
    sg.resolve_relationships()
    assert dict(sg.relationships) == expected


def test_generate_enum(reflected_data, sorted_tables):
    sg = SQLModelSchemaGenerator(reflected_data, sorted_tables, schema="public")

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


def test_declarative_schema_generate(reflected_data, sorted_tables, sqlmodel_tables):
    sg = SQLModelSchemaGenerator(reflected_data, sorted_tables, schema="public")

    assert sg.generate() == sqlmodel_tables
