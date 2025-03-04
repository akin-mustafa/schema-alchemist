import pytest
from sqlalchemy import Column, INTEGER, VARCHAR, TIMESTAMP, Enum, TEXT, ARRAY, NUMERIC
from sqlalchemy.engine.reflection import _ReflectionInfo

from schema_alchemist.generators import BaseGenerator


class DummyGenerator(BaseGenerator):
    klass = Column

    def generate(self, *args, **kwargs):
        return "generated"


@pytest.fixture
def dummy_generator(import_path_resolver):
    return DummyGenerator(import_path_resolver=import_path_resolver)


@pytest.fixture
def reflected_data():
    return _ReflectionInfo(
        columns={
            ("public", "categories"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": "nextval('\"public\".categories_id_seq'::regclass)",
                    "autoincrement": True,
                    "comment": None,
                },
                {
                    "name": "name",
                    "type": VARCHAR(length=100),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "parent_id",
                    "type": INTEGER(),
                    "nullable": True,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "courses"): [
                {
                    "name": "course_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": "nextval('\"public\".courses_course_id_seq'::regclass)",
                    "autoincrement": True,
                    "comment": None,
                },
                {
                    "name": "course_name",
                    "type": VARCHAR(length=100),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "employee_relationships"): [
                {
                    "name": "employee_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "related_employee_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "employees"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": "nextval('\"public\".employees_id_seq'::regclass)",
                    "autoincrement": True,
                    "comment": None,
                },
                {
                    "name": "name",
                    "type": TEXT(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "instructors"): [
                {
                    "name": "instructor_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": "nextval('\"public\".instructors_instructor_id_seq'::regclass)",
                    "autoincrement": True,
                    "comment": None,
                },
                {
                    "name": "name",
                    "type": VARCHAR(length=100),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "email",
                    "type": VARCHAR(length=100),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "order_items"): [
                {
                    "name": "order_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "product_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "quantity",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": "1",
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "unit_price",
                    "type": NUMERIC(precision=10, scale=2),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "orders"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": "nextval('\"public\".orders_id_seq'::regclass)",
                    "autoincrement": True,
                    "comment": None,
                },
                {
                    "name": "user_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "order_date",
                    "type": TIMESTAMP(),
                    "nullable": False,
                    "default": "now()",
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "status",
                    "type": Enum(
                        "pending", "paid", "cancelled", "shipped", name="order_status"
                    ),
                    "nullable": False,
                    "default": "'pending'::order_status",
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "subtotal",
                    "type": NUMERIC(precision=10, scale=2),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "tax",
                    "type": NUMERIC(precision=10, scale=2),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "total",
                    "type": NUMERIC(precision=10, scale=2),
                    "nullable": True,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                    "computed": {"sqltext": "(subtotal + tax)", "persisted": True},
                },
            ],
            ("public", "product_categories"): [
                {
                    "name": "product_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "category_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "products"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": "nextval('\"public\".products_id_seq'::regclass)",
                    "autoincrement": True,
                    "comment": None,
                },
                {
                    "name": "name",
                    "type": VARCHAR(length=255),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "description",
                    "type": TEXT(),
                    "nullable": True,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "price",
                    "type": NUMERIC(precision=10, scale=2),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "tags",
                    "type": ARRAY(TEXT()),
                    "nullable": True,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "profiles"): [
                {
                    "name": "user_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "bio",
                    "type": TEXT(),
                    "nullable": True,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "website",
                    "type": VARCHAR(length=255),
                    "nullable": True,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "student_course_instructors"): [
                {
                    "name": "student_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "course_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "instructor_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "students"): [
                {
                    "name": "student_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": "nextval('\"public\".students_student_id_seq'::regclass)",
                    "autoincrement": True,
                    "comment": None,
                },
                {
                    "name": "name",
                    "type": VARCHAR(length=100),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
                {
                    "name": "email",
                    "type": VARCHAR(length=100),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            ("public", "users"): [
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
                    "type": Enum("admin", "user", "guest", name="user_role"),
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
        },
        pk_constraint={
            ("public", "categories"): {
                "constrained_columns": ["id"],
                "name": "categories_pkey",
                "comment": None,
            },
            ("public", "users"): {
                "constrained_columns": ["id"],
                "name": "users_pkey",
                "comment": None,
            },
            ("public", "profiles"): {
                "constrained_columns": ["user_id"],
                "name": "profiles_pkey",
                "comment": None,
            },
            ("public", "orders"): {
                "constrained_columns": ["id"],
                "name": "orders_pkey",
                "comment": None,
            },
            ("public", "order_items"): {
                "constrained_columns": ["order_id", "product_id"],
                "name": "order_items_pkey",
                "comment": None,
            },
            ("public", "products"): {
                "constrained_columns": ["id"],
                "name": "products_pkey",
                "comment": None,
            },
            ("public", "product_categories"): {
                "constrained_columns": ["product_id", "category_id"],
                "name": "product_categories_pkey",
                "comment": None,
            },
            ("public", "employees"): {
                "constrained_columns": ["id"],
                "name": "employees_pkey",
                "comment": None,
            },
            ("public", "employee_relationships"): {
                "constrained_columns": ["employee_id", "related_employee_id"],
                "name": "employee_relationships_pkey",
                "comment": None,
            },
        },
        foreign_keys={
            ("public", "categories"): [
                {
                    "name": "fk_categories_parent",
                    "constrained_columns": ["parent_id"],
                    "referred_schema": "public",
                    "referred_table": "categories",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "SET NULL"},
                    "comment": None,
                }
            ],
            ("public", "courses"): [],
            ("public", "employee_relationships"): [
                {
                    "name": "fk_employee",
                    "constrained_columns": ["employee_id"],
                    "referred_schema": "public",
                    "referred_table": "employees",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
                {
                    "name": "fk_related_employee",
                    "constrained_columns": ["related_employee_id"],
                    "referred_schema": "public",
                    "referred_table": "employees",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
            ],
            ("public", "employees"): [],
            ("public", "instructors"): [],
            ("public", "order_items"): [
                {
                    "name": "fk_order",
                    "constrained_columns": ["order_id"],
                    "referred_schema": "public",
                    "referred_table": "orders",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
                {
                    "name": "fk_product",
                    "constrained_columns": ["product_id"],
                    "referred_schema": "public",
                    "referred_table": "products",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
            ],
            ("public", "orders"): [
                {
                    "name": "fk_user_order",
                    "constrained_columns": ["user_id"],
                    "referred_schema": "public",
                    "referred_table": "users",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                }
            ],
            ("public", "product_categories"): [
                {
                    "name": "fk_category",
                    "constrained_columns": ["category_id"],
                    "referred_schema": "public",
                    "referred_table": "categories",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
                {
                    "name": "fk_product_category",
                    "constrained_columns": ["product_id"],
                    "referred_schema": "public",
                    "referred_table": "products",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
            ],
            ("public", "products"): [],
            ("public", "profiles"): [
                {
                    "name": "fk_user",
                    "constrained_columns": ["user_id"],
                    "referred_schema": "public",
                    "referred_table": "users",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                }
            ],
            ("public", "student_course_instructors"): [
                {
                    "name": "student_course_instructors_course_id_fkey",
                    "constrained_columns": ["course_id"],
                    "referred_schema": "public",
                    "referred_table": "courses",
                    "referred_columns": ["course_id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
                {
                    "name": "student_course_instructors_instructor_id_fkey",
                    "constrained_columns": ["instructor_id"],
                    "referred_schema": "public",
                    "referred_table": "instructors",
                    "referred_columns": ["instructor_id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
                {
                    "name": "student_course_instructors_student_id_fkey",
                    "constrained_columns": ["student_id"],
                    "referred_schema": "public",
                    "referred_table": "students",
                    "referred_columns": ["student_id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
            ],
            ("public", "students"): [],
            ("public", "users"): [],
        },
        indexes={
            ("public", "categories"): [
                {
                    "name": "category_name_idx",
                    "unique": False,
                    "column_names": ["name"],
                    "include_columns": [],
                    "dialect_options": {"postgresql_include": []},
                },
                {
                    "name": "categories_name_key",
                    "unique": True,
                    "column_names": ["name"],
                    "duplicates_constraint": "categories_name_key",
                    "include_columns": [],
                    "dialect_options": {"postgresql_include": []},
                },
            ],
            ("public", "users"): [
                {
                    "name": "users_email_key",
                    "unique": True,
                    "column_names": ["email"],
                    "duplicates_constraint": "users_email_key",
                    "include_columns": [],
                    "dialect_options": {"postgresql_include": []},
                }
            ],
            ("public", "profiles"): [],
            ("public", "orders"): [],
            ("public", "order_items"): [],
            ("public", "products"): [],
            ("public", "product_categories"): [],
            ("public", "employees"): [],
            ("public", "employee_relationships"): [],
        },
        unique_constraints={
            ("public", "categories"): [
                {
                    "column_names": ["name"],
                    "name": "categories_name_key",
                    "comment": None,
                }
            ],
            ("public", "users"): [
                {"column_names": ["email"], "name": "users_email_key", "comment": None}
            ],
            ("public", "profiles"): [],
            ("public", "orders"): [],
            ("public", "order_items"): [],
            ("public", "products"): [],
            ("public", "product_categories"): [],
            ("public", "employees"): [],
            ("public", "employee_relationships"): [],
        },
        table_comment={
            ("public", "categories"): {"text": None},
            ("public", "users"): {"text": None},
            ("public", "profiles"): {"text": None},
            ("public", "orders"): {"text": None},
            ("public", "order_items"): {"text": None},
            ("public", "products"): {"text": None},
            ("public", "product_categories"): {"text": None},
            ("public", "employees"): {"text": None},
            ("public", "employee_relationships"): {"text": None},
            ("public", "students"): {"text": None},
            ("public", "student_course_instructors"): {"text": None},
            ("public", "courses"): {"text": None},
            ("public", "instructors"): {"text": None},
        },
        check_constraints={
            ("public", "categories"): [],
            ("public", "courses"): [],
            ("public", "employee_relationships"): [],
            ("public", "employees"): [],
            ("public", "instructors"): [],
            ("public", "order_items"): [
                {
                    "name": "order_items_quantity_check",
                    "sqltext": "quantity > 0",
                    "comment": None,
                },
                {
                    "name": "order_items_unit_price_check",
                    "sqltext": "unit_price >= 0::numeric",
                    "comment": None,
                },
            ],
            ("public", "orders"): [
                {
                    "name": "orders_subtotal_check",
                    "sqltext": "subtotal >= 0::numeric",
                    "comment": None,
                },
                {
                    "name": "orders_tax_check",
                    "sqltext": "tax >= 0::numeric",
                    "comment": None,
                },
            ],
            ("public", "product_categories"): [],
            ("public", "products"): [
                {
                    "name": "products_price_check",
                    "sqltext": "price >= 0::numeric",
                    "comment": None,
                }
            ],
            ("public", "profiles"): [],
            ("public", "student_course_instructors"): [],
            ("public", "students"): [],
            ("public", "users"): [],
        },
        table_options={},
        unreflectable={},
    )


@pytest.fixture
def sorted_tables():
    return [
        ("categories", [("categories", "fk_categories_parent")]),
        ("courses", []),
        ("employees", []),
        ("instructors", []),
        ("products", []),
        ("students", []),
        ("users", []),
        (
            "employee_relationships",
            [
                ("employee_relationships", "fk_related_employee"),
                ("employee_relationships", "fk_employee"),
            ],
        ),
        ("orders", [("orders", "fk_user_order")]),
        (
            "product_categories",
            [
                ("product_categories", "fk_product_category"),
                ("product_categories", "fk_category"),
            ],
        ),
        ("profiles", [("profiles", "fk_user")]),
        (
            "student_course_instructors",
            [
                (
                    "student_course_instructors",
                    "student_course_instructors_instructor_id_fkey",
                ),
                (
                    "student_course_instructors",
                    "student_course_instructors_student_id_fkey",
                ),
                (
                    "student_course_instructors",
                    "student_course_instructors_course_id_fkey",
                ),
            ],
        ),
        ("order_items", [("order_items", "fk_order"), ("order_items", "fk_product")]),
        (None, []),
    ]


@pytest.fixture(scope="session")
def core_table():
    return """from datetime import datetime
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
)


metadata = MetaData(schema='public')


Categories = Table('categories', metadata,
    Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".categories_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=100), autoincrement=False, index=True, unique=True, nullable=False),
    Column('parent_id', INTEGER(), autoincrement=False, nullable=True),

    PrimaryKeyConstraint('id', name='categories_pkey'),
    ForeignKeyConstraint(columns=['parent_id'], refcolumns=['public.categories.id'], name='fk_categories_parent', ondelete='SET NULL'),
    Index('category_name_idx', 'name'),
    UniqueConstraint('name', name='categories_name_key'),
    schema = 'public'
)


Courses = Table('courses', metadata,
    Column('course_id', INTEGER(), autoincrement=True, nullable=False, server_default='nextval(\\'"public".courses_course_id_seq\\'::regclass)'),
    Column('course_name', VARCHAR(length=100), autoincrement=False, nullable=False),

    schema = 'public'
)


Employees = Table('employees', metadata,
    Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".employees_id_seq\\'::regclass)'),
    Column('name', TEXT(), autoincrement=False, nullable=False),

    PrimaryKeyConstraint('id', name='employees_pkey'),
    schema = 'public'
)


Instructors = Table('instructors', metadata,
    Column('instructor_id', INTEGER(), autoincrement=True, nullable=False, server_default='nextval(\\'"public".instructors_instructor_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('email', VARCHAR(length=100), autoincrement=False, nullable=False),

    schema = 'public'
)


Products = Table('products', metadata,
    Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".products_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=255), autoincrement=False, nullable=False),
    Column('description', TEXT(), autoincrement=False, nullable=True),
    Column('price', NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    Column('tags', ARRAY(TEXT()), autoincrement=False, nullable=True),

    PrimaryKeyConstraint('id', name='products_pkey'),
    CheckConstraint(sqltext='price >= 0::numeric', name='products_price_check'),
    schema = 'public'
)


Students = Table('students', metadata,
    Column('student_id', INTEGER(), autoincrement=True, nullable=False, server_default='nextval(\\'"public".students_student_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('email', VARCHAR(length=100), autoincrement=False, nullable=False),

    schema = 'public'
)


Users = Table('users', metadata,
    Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".users_id_seq\\'::regclass)'),
    Column('first_name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('last_name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('full_name', VARCHAR(length=201), Computed(sqltext="(((first_name)::text || ' '::text) || (last_name)::text)", persisted=True), autoincrement=False, nullable=True),
    Column('email', VARCHAR(length=255), autoincrement=False, unique=True, nullable=False),
    Column('role', sqltypes_Enum('admin', 'user', 'guest', name='user_role'), autoincrement=False, nullable=False, server_default="'user'::user_role"),
    Column('phone_numbers', ARRAY(TEXT()), autoincrement=False, nullable=True),

    PrimaryKeyConstraint('id', name='users_pkey'),
    UniqueConstraint('email', name='users_email_key'),
    schema = 'public'
)


EmployeeRelationships = Table('employee_relationships', metadata,
    Column('employee_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('related_employee_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),

    PrimaryKeyConstraint('employee_id', 'related_employee_id', name='employee_relationships_pkey'),
    ForeignKeyConstraint(columns=['employee_id'], refcolumns=['public.employees.id'], name='fk_employee', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['related_employee_id'], refcolumns=['public.employees.id'], name='fk_related_employee', ondelete='CASCADE'),
    schema = 'public'
)


Orders = Table('orders', metadata,
    Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".orders_id_seq\\'::regclass)'),
    Column('user_id', INTEGER(), autoincrement=False, nullable=False),
    Column('order_date', TIMESTAMP(), autoincrement=False, nullable=False, server_default='now()'),
    Column('status', sqltypes_Enum('pending', 'paid', 'cancelled', 'shipped', name='order_status'), autoincrement=False, nullable=False, server_default="'pending'::order_status"),
    Column('subtotal', NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    Column('tax', NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    Column('total', NUMERIC(precision=10, scale=2), Computed(sqltext='(subtotal + tax)', persisted=True), autoincrement=False, nullable=True),

    PrimaryKeyConstraint('id', name='orders_pkey'),
    ForeignKeyConstraint(columns=['user_id'], refcolumns=['public.users.id'], name='fk_user_order', ondelete='CASCADE'),
    CheckConstraint(sqltext='subtotal >= 0::numeric', name='orders_subtotal_check'),
    CheckConstraint(sqltext='tax >= 0::numeric', name='orders_tax_check'),
    schema = 'public'
)


ProductCategories = Table('product_categories', metadata,
    Column('product_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('category_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),

    PrimaryKeyConstraint('product_id', 'category_id', name='product_categories_pkey'),
    ForeignKeyConstraint(columns=['category_id'], refcolumns=['public.categories.id'], name='fk_category', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['product_id'], refcolumns=['public.products.id'], name='fk_product_category', ondelete='CASCADE'),
    schema = 'public'
)


Profiles = Table('profiles', metadata,
    Column('user_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('bio', TEXT(), autoincrement=False, nullable=True),
    Column('website', VARCHAR(length=255), autoincrement=False, nullable=True),

    PrimaryKeyConstraint('user_id', name='profiles_pkey'),
    ForeignKeyConstraint(columns=['user_id'], refcolumns=['public.users.id'], name='fk_user', ondelete='CASCADE'),
    schema = 'public'
)


StudentCourseInstructors = Table('student_course_instructors', metadata,
    Column('student_id', INTEGER(), autoincrement=False, nullable=False),
    Column('course_id', INTEGER(), autoincrement=False, nullable=False),
    Column('instructor_id', INTEGER(), autoincrement=False, nullable=False),

    ForeignKeyConstraint(columns=['course_id'], refcolumns=['public.courses.course_id'], name='student_course_instructors_course_id_fkey', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['instructor_id'], refcolumns=['public.instructors.instructor_id'], name='student_course_instructors_instructor_id_fkey', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['student_id'], refcolumns=['public.students.student_id'], name='student_course_instructors_student_id_fkey', ondelete='CASCADE'),
    schema = 'public'
)


OrderItems = Table('order_items', metadata,
    Column('order_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('product_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('quantity', INTEGER(), autoincrement=False, nullable=False, server_default='1'),
    Column('unit_price', NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),

    PrimaryKeyConstraint('order_id', 'product_id', name='order_items_pkey'),
    ForeignKeyConstraint(columns=['order_id'], refcolumns=['public.orders.id'], name='fk_order', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['product_id'], refcolumns=['public.products.id'], name='fk_product', ondelete='CASCADE'),
    CheckConstraint(sqltext='quantity > 0', name='order_items_quantity_check'),
    CheckConstraint(sqltext='unit_price >= 0::numeric', name='order_items_unit_price_check'),
    schema = 'public'
)"""


@pytest.fixture(scope="session")
def declarative_table():
    return """from datetime import datetime
from decimal import Decimal
from enum import Enum as enum_Enum
from sqlalchemy.orm._orm_constructors import (
    mapped_column,
    relationship
)
from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm.decl_api import DeclarativeBase
from sqlalchemy.sql.schema import (
    CheckConstraint,
    Column,
    Computed,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
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
)


class order_status(enum_Enum):
    pending = 'pending'
    paid = 'paid'
    cancelled = 'cancelled'
    shipped = 'shipped'


class user_role(enum_Enum):
    admin = 'admin'
    user = 'user'
    guest = 'guest'


class Base(DeclarativeBase):
    pass


class OrderItems(Base):
    __tablename__ = 'order_items'
    __table_args__ = (
        PrimaryKeyConstraint('order_id', 'product_id', name='order_items_pkey'),
        ForeignKeyConstraint(columns=['order_id'], refcolumns=['public.orders.id'], name='fk_order', ondelete='CASCADE'),
        ForeignKeyConstraint(columns=['product_id'], refcolumns=['public.products.id'], name='fk_product', ondelete='CASCADE'),
        CheckConstraint(sqltext='quantity > 0', name='order_items_quantity_check'),
        CheckConstraint(sqltext='unit_price >= 0::numeric', name='order_items_unit_price_check'),
        {'schema': 'public'}
    )

    order_id: Mapped[int] = mapped_column('order_id', INTEGER(), nullable=False, primary_key=True, autoincrement=False)
    product_id: Mapped[int] = mapped_column('product_id', INTEGER(), nullable=False, primary_key=True, autoincrement=False)
    quantity: Mapped[int] = mapped_column('quantity', INTEGER(), nullable=False, autoincrement=False, server_default='1')
    unit_price: Mapped[Decimal] = mapped_column('unit_price', NUMERIC(precision=10, scale=2), nullable=False, autoincrement=False)

    order: Mapped['Orders'] = relationship(back_populates='order_items', foreign_keys='[OrderItems.order_id,]')
    product: Mapped['Products'] = relationship(back_populates='order_items', foreign_keys='[OrderItems.product_id,]')


StudentCourseInstructors = Table('student_course_instructors', Base,
    Column('student_id', INTEGER(), autoincrement=False, nullable=False),
    Column('course_id', INTEGER(), autoincrement=False, nullable=False),
    Column('instructor_id', INTEGER(), autoincrement=False, nullable=False),

    ForeignKeyConstraint(columns=['course_id'], refcolumns=['public.courses.course_id'], name='student_course_instructors_course_id_fkey', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['instructor_id'], refcolumns=['public.instructors.instructor_id'], name='student_course_instructors_instructor_id_fkey', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['student_id'], refcolumns=['public.students.student_id'], name='student_course_instructors_student_id_fkey', ondelete='CASCADE'),
    schema = 'public'
)


class Profiles(Base):
    __tablename__ = 'profiles'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='profiles_pkey'),
        ForeignKeyConstraint(columns=['user_id'], refcolumns=['public.users.id'], name='fk_user', ondelete='CASCADE'),
        {'schema': 'public'}
    )

    user_id: Mapped[int] = mapped_column('user_id', INTEGER(), nullable=False, primary_key=True, autoincrement=False)
    bio: Mapped[Optional[str]] = mapped_column('bio', TEXT(), nullable=True, autoincrement=False)
    website: Mapped[Optional[str]] = mapped_column('website', VARCHAR(length=255), nullable=True, autoincrement=False)

    user: Mapped['Users'] = relationship(back_populates='profile', foreign_keys='[Profiles.user_id,]')


ProductCategories = Table('product_categories', Base,
    Column('product_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('category_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),

    PrimaryKeyConstraint('product_id', 'category_id', name='product_categories_pkey'),
    ForeignKeyConstraint(columns=['category_id'], refcolumns=['public.categories.id'], name='fk_category', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['product_id'], refcolumns=['public.products.id'], name='fk_product_category', ondelete='CASCADE'),
    schema = 'public'
)


class Orders(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='orders_pkey'),
        ForeignKeyConstraint(columns=['user_id'], refcolumns=['public.users.id'], name='fk_user_order', ondelete='CASCADE'),
        CheckConstraint(sqltext='subtotal >= 0::numeric', name='orders_subtotal_check'),
        CheckConstraint(sqltext='tax >= 0::numeric', name='orders_tax_check'),
        {'schema': 'public'}
    )

    id: Mapped[int] = mapped_column('id', INTEGER(), nullable=False, primary_key=True, autoincrement=True, server_default='nextval(\\'"public".orders_id_seq\\'::regclass)')
    user_id: Mapped[int] = mapped_column('user_id', INTEGER(), nullable=False, autoincrement=False)
    order_date: Mapped[datetime] = mapped_column('order_date', TIMESTAMP(), nullable=False, autoincrement=False, server_default='now()')
    status: Mapped[order_status] = mapped_column('status', sqltypes_Enum('pending', 'paid', 'cancelled', 'shipped', name='order_status'), nullable=False, autoincrement=False, server_default="'pending'::order_status")
    subtotal: Mapped[Decimal] = mapped_column('subtotal', NUMERIC(precision=10, scale=2), nullable=False, autoincrement=False)
    tax: Mapped[Decimal] = mapped_column('tax', NUMERIC(precision=10, scale=2), nullable=False, autoincrement=False)
    total: Mapped[Optional[Decimal]] = mapped_column('total', NUMERIC(precision=10, scale=2), Computed(sqltext='(subtotal + tax)', persisted=True), nullable=True, autoincrement=False)

    order_items: Mapped[List['OrderItems']] = relationship(back_populates='order', foreign_keys='[OrderItems.order_id,]')
    user: Mapped['Users'] = relationship(back_populates='orders', foreign_keys='[Orders.user_id,]')


EmployeeRelationships = Table('employee_relationships', Base,
    Column('employee_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('related_employee_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),

    PrimaryKeyConstraint('employee_id', 'related_employee_id', name='employee_relationships_pkey'),
    ForeignKeyConstraint(columns=['employee_id'], refcolumns=['public.employees.id'], name='fk_employee', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['related_employee_id'], refcolumns=['public.employees.id'], name='fk_related_employee', ondelete='CASCADE'),
    schema = 'public'
)


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        {'schema': 'public'}
    )

    id: Mapped[int] = mapped_column('id', INTEGER(), nullable=False, primary_key=True, autoincrement=True, server_default='nextval(\\'"public".users_id_seq\\'::regclass)')
    first_name: Mapped[str] = mapped_column('first_name', VARCHAR(length=100), nullable=False, autoincrement=False)
    last_name: Mapped[str] = mapped_column('last_name', VARCHAR(length=100), nullable=False, autoincrement=False)
    full_name: Mapped[Optional[str]] = mapped_column('full_name', VARCHAR(length=201), Computed(sqltext="(((first_name)::text || ' '::text) || (last_name)::text)", persisted=True), nullable=True, autoincrement=False)
    email: Mapped[str] = mapped_column('email', VARCHAR(length=255), nullable=False, autoincrement=False, unique=True)
    role: Mapped[user_role] = mapped_column('role', sqltypes_Enum('admin', 'user', 'guest', name='user_role'), nullable=False, autoincrement=False, server_default="'user'::user_role")
    phone_numbers: Mapped[Optional[List]] = mapped_column('phone_numbers', ARRAY(TEXT()), nullable=True, autoincrement=False)

    orders: Mapped[List['Orders']] = relationship(back_populates='user', foreign_keys='[Orders.user_id,]')
    profile: Mapped['Profiles'] = relationship(back_populates='user', foreign_keys='[Profiles.user_id,]')


Students = Table('students', Base,
    Column('student_id', INTEGER(), autoincrement=True, nullable=False, server_default='nextval(\\'"public".students_student_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('email', VARCHAR(length=100), autoincrement=False, nullable=False),

    schema = 'public'
)


class Products(Base):
    __tablename__ = 'products'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='products_pkey'),
        CheckConstraint(sqltext='price >= 0::numeric', name='products_price_check'),
        {'schema': 'public'}
    )

    id: Mapped[int] = mapped_column('id', INTEGER(), nullable=False, primary_key=True, autoincrement=True, server_default='nextval(\\'"public".products_id_seq\\'::regclass)')
    name: Mapped[str] = mapped_column('name', VARCHAR(length=255), nullable=False, autoincrement=False)
    description: Mapped[Optional[str]] = mapped_column('description', TEXT(), nullable=True, autoincrement=False)
    price: Mapped[Decimal] = mapped_column('price', NUMERIC(precision=10, scale=2), nullable=False, autoincrement=False)
    tags: Mapped[Optional[List]] = mapped_column('tags', ARRAY(TEXT()), nullable=True, autoincrement=False)

    order_items: Mapped[List['OrderItems']] = relationship(back_populates='product', foreign_keys='[OrderItems.product_id,]')
    categories: Mapped[List['Categories']] = relationship(secondary=ProductCategories, back_populates='products')


Instructors = Table('instructors', Base,
    Column('instructor_id', INTEGER(), autoincrement=True, nullable=False, server_default='nextval(\\'"public".instructors_instructor_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('email', VARCHAR(length=100), autoincrement=False, nullable=False),

    schema = 'public'
)


class Employees(Base):
    __tablename__ = 'employees'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='employees_pkey'),
        {'schema': 'public'}
    )

    id: Mapped[int] = mapped_column('id', INTEGER(), nullable=False, primary_key=True, autoincrement=True, server_default='nextval(\\'"public".employees_id_seq\\'::regclass)')
    name: Mapped[str] = mapped_column('name', TEXT(), nullable=False, autoincrement=False)

    related_employees: Mapped[List['Employees']] = relationship(secondary=EmployeeRelationships, primaryjoin=id == EmployeeRelationships.c.employee_id, secondaryjoin=id == EmployeeRelationships.c.related_employee_id, back_populates='employees')
    employees: Mapped[List['Employees']] = relationship(secondary=EmployeeRelationships, primaryjoin=id == EmployeeRelationships.c.related_employee_id, secondaryjoin=id == EmployeeRelationships.c.employee_id, back_populates='related_employees')


Courses = Table('courses', Base,
    Column('course_id', INTEGER(), autoincrement=True, nullable=False, server_default='nextval(\\'"public".courses_course_id_seq\\'::regclass)'),
    Column('course_name', VARCHAR(length=100), autoincrement=False, nullable=False),

    schema = 'public'
)


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='categories_pkey'),
        ForeignKeyConstraint(columns=['parent_id'], refcolumns=['public.categories.id'], name='fk_categories_parent', ondelete='SET NULL'),
        Index('category_name_idx', 'name'),
        UniqueConstraint('name', name='categories_name_key'),
        {'schema': 'public'}
    )

    id: Mapped[int] = mapped_column('id', INTEGER(), nullable=False, primary_key=True, autoincrement=True, server_default='nextval(\\'"public".categories_id_seq\\'::regclass)')
    name: Mapped[str] = mapped_column('name', VARCHAR(length=100), nullable=False, autoincrement=False, index=True, unique=True)
    parent_id: Mapped[Optional[int]] = mapped_column('parent_id', INTEGER(), nullable=True, autoincrement=False)

    parent: Mapped['Categories'] = relationship(back_populates='sub_categories', foreign_keys='[Categories.parent_id,]', remote_side='Categories.id')
    sub_categories: Mapped[List['Categories']] = relationship(back_populates='parent', foreign_keys='[Categories.parent_id,]')
    products: Mapped[List['Products']] = relationship(secondary=ProductCategories, back_populates='categories')"""


@pytest.fixture(scope="session")
def sqlmodel_tables():
    return """from datetime import datetime
from decimal import Decimal
from enum import Enum as enum_Enum
from sqlalchemy.orm.decl_api import registry
from sqlalchemy.sql.schema import (
    CheckConstraint,
    Column,
    Computed,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
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
from sqlmodel.main import (
    Field,
    Relationship,
    SQLModel
)
from typing import (
    List,
    Optional
)


class order_status(enum_Enum):
    pending = 'pending'
    paid = 'paid'
    cancelled = 'cancelled'
    shipped = 'shipped'


class user_role(enum_Enum):
    admin = 'admin'
    user = 'user'
    guest = 'guest'


class Base(SQLModel, registry=registry()):
    pass


class OrderItems(Base, table=True):
    __tablename__ = 'order_items'
    __table_args__ = (
        PrimaryKeyConstraint('order_id', 'product_id', name='order_items_pkey'),
        ForeignKeyConstraint(columns=['order_id'], refcolumns=['public.orders.id'], name='fk_order', ondelete='CASCADE'),
        ForeignKeyConstraint(columns=['product_id'], refcolumns=['public.products.id'], name='fk_product', ondelete='CASCADE'),
        CheckConstraint(sqltext='quantity > 0', name='order_items_quantity_check'),
        CheckConstraint(sqltext='unit_price >= 0::numeric', name='order_items_unit_price_check'),
        {'schema': 'public'}
    )

    order_id: Optional[int] = Field(default=None, sa_column=Column('order_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True))
    product_id: Optional[int] = Field(default=None, sa_column=Column('product_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True))
    quantity: int = Field(sa_column=Column('quantity', INTEGER(), autoincrement=False, nullable=False, server_default='1'))
    unit_price: Decimal = Field(sa_column=Column('unit_price', NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))

    order: 'Orders' = Relationship(back_populates='order_items', sa_relationship_kwargs={'foreign_keys': '[OrderItems.order_id,]'})
    product: 'Products' = Relationship(back_populates='order_items', sa_relationship_kwargs={'foreign_keys': '[OrderItems.product_id,]'})


StudentCourseInstructors = Table('student_course_instructors', Base.metadata,
    Column('student_id', INTEGER(), autoincrement=False, nullable=False),
    Column('course_id', INTEGER(), autoincrement=False, nullable=False),
    Column('instructor_id', INTEGER(), autoincrement=False, nullable=False),

    ForeignKeyConstraint(columns=['course_id'], refcolumns=['public.courses.course_id'], name='student_course_instructors_course_id_fkey', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['instructor_id'], refcolumns=['public.instructors.instructor_id'], name='student_course_instructors_instructor_id_fkey', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['student_id'], refcolumns=['public.students.student_id'], name='student_course_instructors_student_id_fkey', ondelete='CASCADE'),
    schema = 'public'
)


class Profiles(Base, table=True):
    __tablename__ = 'profiles'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='profiles_pkey'),
        ForeignKeyConstraint(columns=['user_id'], refcolumns=['public.users.id'], name='fk_user', ondelete='CASCADE'),
        {'schema': 'public'}
    )

    user_id: Optional[int] = Field(default=None, sa_column=Column('user_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True))
    bio: Optional[str] = Field(default=None, sa_column=Column('bio', TEXT(), autoincrement=False, nullable=True))
    website: Optional[str] = Field(default=None, sa_column=Column('website', VARCHAR(length=255), autoincrement=False, nullable=True))

    user: 'Users' = Relationship(back_populates='profile', sa_relationship_kwargs={'foreign_keys': '[Profiles.user_id,]'})


ProductCategories = Table('product_categories', Base.metadata,
    Column('product_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('category_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),

    PrimaryKeyConstraint('product_id', 'category_id', name='product_categories_pkey'),
    ForeignKeyConstraint(columns=['category_id'], refcolumns=['public.categories.id'], name='fk_category', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['product_id'], refcolumns=['public.products.id'], name='fk_product_category', ondelete='CASCADE'),
    schema = 'public'
)


class Orders(Base, table=True):
    __tablename__ = 'orders'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='orders_pkey'),
        ForeignKeyConstraint(columns=['user_id'], refcolumns=['public.users.id'], name='fk_user_order', ondelete='CASCADE'),
        CheckConstraint(sqltext='subtotal >= 0::numeric', name='orders_subtotal_check'),
        CheckConstraint(sqltext='tax >= 0::numeric', name='orders_tax_check'),
        {'schema': 'public'}
    )

    id: Optional[int] = Field(default=None, sa_column=Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".orders_id_seq\\'::regclass)'))
    user_id: int = Field(sa_column=Column('user_id', INTEGER(), autoincrement=False, nullable=False))
    order_date: datetime = Field(sa_column=Column('order_date', TIMESTAMP(), autoincrement=False, nullable=False, server_default='now()'))
    status: order_status = Field(sa_column=Column('status', sqltypes_Enum('pending', 'paid', 'cancelled', 'shipped', name='order_status'), autoincrement=False, nullable=False, server_default="'pending'::order_status"))
    subtotal: Decimal = Field(sa_column=Column('subtotal', NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))
    tax: Decimal = Field(sa_column=Column('tax', NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))
    total: Optional[Decimal] = Field(default=None, sa_column=Column('total', NUMERIC(precision=10, scale=2), Computed(sqltext='(subtotal + tax)', persisted=True), autoincrement=False, nullable=True))

    order_items: List['OrderItems'] = Relationship(back_populates='order', sa_relationship_kwargs={'foreign_keys': '[OrderItems.order_id,]'})
    user: 'Users' = Relationship(back_populates='orders', sa_relationship_kwargs={'foreign_keys': '[Orders.user_id,]'})


EmployeeRelationships = Table('employee_relationships', Base.metadata,
    Column('employee_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('related_employee_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),

    PrimaryKeyConstraint('employee_id', 'related_employee_id', name='employee_relationships_pkey'),
    ForeignKeyConstraint(columns=['employee_id'], refcolumns=['public.employees.id'], name='fk_employee', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['related_employee_id'], refcolumns=['public.employees.id'], name='fk_related_employee', ondelete='CASCADE'),
    schema = 'public'
)


class Users(Base, table=True):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        {'schema': 'public'}
    )

    id: Optional[int] = Field(default=None, sa_column=Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".users_id_seq\\'::regclass)'))
    first_name: str = Field(sa_column=Column('first_name', VARCHAR(length=100), autoincrement=False, nullable=False))
    last_name: str = Field(sa_column=Column('last_name', VARCHAR(length=100), autoincrement=False, nullable=False))
    full_name: Optional[str] = Field(default=None, sa_column=Column('full_name', VARCHAR(length=201), Computed(sqltext="(((first_name)::text || ' '::text) || (last_name)::text)", persisted=True), autoincrement=False, nullable=True))
    email: str = Field(sa_column=Column('email', VARCHAR(length=255), autoincrement=False, unique=True, nullable=False))
    role: user_role = Field(sa_column=Column('role', sqltypes_Enum('admin', 'user', 'guest', name='user_role'), autoincrement=False, nullable=False, server_default="'user'::user_role"))
    phone_numbers: Optional[List] = Field(default=None, sa_column=Column('phone_numbers', ARRAY(TEXT()), autoincrement=False, nullable=True))

    orders: List['Orders'] = Relationship(back_populates='user', sa_relationship_kwargs={'foreign_keys': '[Orders.user_id,]'})
    profile: 'Profiles' = Relationship(back_populates='user', sa_relationship_kwargs={'foreign_keys': '[Profiles.user_id,]'})


Students = Table('students', Base.metadata,
    Column('student_id', INTEGER(), autoincrement=True, nullable=False, server_default='nextval(\\'"public".students_student_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('email', VARCHAR(length=100), autoincrement=False, nullable=False),

    schema = 'public'
)


class Products(Base, table=True):
    __tablename__ = 'products'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='products_pkey'),
        CheckConstraint(sqltext='price >= 0::numeric', name='products_price_check'),
        {'schema': 'public'}
    )

    id: Optional[int] = Field(default=None, sa_column=Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".products_id_seq\\'::regclass)'))
    name: str = Field(sa_column=Column('name', VARCHAR(length=255), autoincrement=False, nullable=False))
    description: Optional[str] = Field(default=None, sa_column=Column('description', TEXT(), autoincrement=False, nullable=True))
    price: Decimal = Field(sa_column=Column('price', NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))
    tags: Optional[List] = Field(default=None, sa_column=Column('tags', ARRAY(TEXT()), autoincrement=False, nullable=True))

    order_items: List['OrderItems'] = Relationship(back_populates='product', sa_relationship_kwargs={'foreign_keys': '[OrderItems.product_id,]'})
    categories: List['Categories'] = Relationship(back_populates='products', link_model=ProductCategories)


Instructors = Table('instructors', Base.metadata,
    Column('instructor_id', INTEGER(), autoincrement=True, nullable=False, server_default='nextval(\\'"public".instructors_instructor_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=100), autoincrement=False, nullable=False),
    Column('email', VARCHAR(length=100), autoincrement=False, nullable=False),

    schema = 'public'
)


class Employees(Base, table=True):
    __tablename__ = 'employees'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='employees_pkey'),
        {'schema': 'public'}
    )

    id: Optional[int] = Field(default=None, sa_column=Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".employees_id_seq\\'::regclass)'))
    name: str = Field(sa_column=Column('name', TEXT(), autoincrement=False, nullable=False))

    related_employees: List['Employees'] = Relationship(back_populates='employees', link_model=EmployeeRelationships, sa_relationship_kwargs={'primaryjoin': id == EmployeeRelationships.c.employee_id, 'secondaryjoin': id == EmployeeRelationships.c.related_employee_id})
    employees: List['Employees'] = Relationship(back_populates='related_employees', link_model=EmployeeRelationships, sa_relationship_kwargs={'primaryjoin': id == EmployeeRelationships.c.related_employee_id, 'secondaryjoin': id == EmployeeRelationships.c.employee_id})


Courses = Table('courses', Base.metadata,
    Column('course_id', INTEGER(), autoincrement=True, nullable=False, server_default='nextval(\\'"public".courses_course_id_seq\\'::regclass)'),
    Column('course_name', VARCHAR(length=100), autoincrement=False, nullable=False),

    schema = 'public'
)


class Categories(Base, table=True):
    __tablename__ = 'categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='categories_pkey'),
        ForeignKeyConstraint(columns=['parent_id'], refcolumns=['public.categories.id'], name='fk_categories_parent', ondelete='SET NULL'),
        Index('category_name_idx', 'name'),
        UniqueConstraint('name', name='categories_name_key'),
        {'schema': 'public'}
    )

    id: Optional[int] = Field(default=None, sa_column=Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".categories_id_seq\\'::regclass)'))
    name: str = Field(sa_column=Column('name', VARCHAR(length=100), autoincrement=False, index=True, unique=True, nullable=False))
    parent_id: Optional[int] = Field(default=None, sa_column=Column('parent_id', INTEGER(), autoincrement=False, nullable=True))

    parent: 'Categories' = Relationship(back_populates='sub_categories', sa_relationship_kwargs={'remote_side': 'Categories.id', 'foreign_keys': '[Categories.parent_id,]'})
    sub_categories: List['Categories'] = Relationship(back_populates='parent', sa_relationship_kwargs={'foreign_keys': '[Categories.parent_id,]'})
    products: List['Products'] = Relationship(back_populates='categories', link_model=ProductCategories)"""
