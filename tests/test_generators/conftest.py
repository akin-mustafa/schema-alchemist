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
            ("public", "categories"): {
                "constrained_columns": ["id"],
                "name": "categories_pkey",
                "comment": None,
            },
        },
        foreign_keys={
            ("public", "categories"): [],
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
            ("public", "users"): [],
        },
        indexes={
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
        },
        unique_constraints={
            ("public", "users"): [
                {"column_names": ["email"], "name": "users_email_key", "comment": None}
            ],
            ("public", "profiles"): [],
            ("public", "orders"): [],
            ("public", "order_items"): [],
            ("public", "products"): [],
            ("public", "product_categories"): [],
            ("public", "categories"): [
                {
                    "column_names": ["name"],
                    "name": "categories_name_key",
                    "comment": None,
                }
            ],
        },
        table_comment={
            ("public", "users"): {"text": None},
            ("public", "profiles"): {"text": None},
            ("public", "orders"): {"text": None},
            ("public", "order_items"): {"text": None},
            ("public", "products"): {"text": None},
            ("public", "product_categories"): {"text": None},
            ("public", "categories"): {"text": None},
        },
        check_constraints={
            ("public", "categories"): [],
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
            ("public", "users"): [],
        },
        table_options={},
        unreflectable={},
    )


@pytest.fixture
def relationship_reflected_data():
    return _ReflectionInfo(
        columns={
            # m2m products-categories through product_categories
            ("public", "categories"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
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
            ],
            # o2m order_items-orders
            # o2m order_items-products
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
            ],
            # m2o orders-order_items
            # o2m orders-users
            ("public", "orders"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
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
            ],
            # associate table between product and category
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
            # m2m products-categories through product_categories
            # m2o products-order_items
            ("public", "products"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
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
                    "name": "price",
                    "type": NUMERIC(precision=10, scale=2),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            # o2o user-profile
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
                    "name": "website",
                    "type": VARCHAR(length=255),
                    "nullable": True,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            # o2o users-profiles
            # m2o users-orders
            ("public", "users"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
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
            ],
            ("public", "email_addresses"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": True,
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
                {
                    "name": "user_id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": False,
                    "comment": None,
                },
            ],
            # associated table with its own pk for m2m students-course-instructor
            ("public", "student_course_instructors"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
                    "autoincrement": True,
                    "comment": None,
                },
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
            # m2m students-courses-instructors
            ("public", "students"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
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
            ],
            # m2m students-courses-instructors
            ("public", "instructors"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
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
            ],
            # m2m courses-students-instructors
            ("public", "courses"): [
                {
                    "name": "id",
                    "type": INTEGER(),
                    "nullable": False,
                    "default": None,
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
            ],
        },
        pk_constraint={
            ("public", "courses"): {
                "constrained_columns": ["id"],
                "name": "courses_pkey",
                "comment": None,
            },
            ("public", "students"): {
                "constrained_columns": ["id"],
                "name": "students_pkey",
                "comment": None,
            },
            ("public", "instructors"): {
                "constrained_columns": ["id"],
                "name": "instructors_pkey",
                "comment": None,
            },
            ("public", "student_course_instructors"): {
                "constrained_columns": ["id"],
                "name": "student_course_instructors_pkey",
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
            ("public", "email_addresses"): {
                "constrained_columns": ["id"],
                "name": "email_addresses_pkey",
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
            ("public", "categories"): {
                "constrained_columns": ["id"],
                "name": "categories_pkey",
                "comment": None,
            },
        },
        foreign_keys={
            ("public", "categories"): [],
            ("public", "students"): [],
            ("public", "instructors"): [],
            ("public", "courses"): [],
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
            ("public", "email_addresses"): [
                {
                    "name": "fk_user_email_address",
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
                    "name": "fk_student",
                    "constrained_columns": ["student_id"],
                    "referred_schema": "public",
                    "referred_table": "students",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
                {
                    "name": "fk_course",
                    "constrained_columns": ["course_id"],
                    "referred_schema": "public",
                    "referred_table": "courses",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
                {
                    "name": "fk_instructor",
                    "constrained_columns": ["instructor_id"],
                    "referred_schema": "public",
                    "referred_table": "instructors",
                    "referred_columns": ["id"],
                    "options": {"ondelete": "CASCADE"},
                    "comment": None,
                },
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
            ("public", "users"): [],
        },
        indexes={},
        unique_constraints={
            ("public", "email_addresses"): [
                {
                    "column_names": ["email"],
                    "name": "email_addresses_email_key",
                    "comment": None,
                },
                {
                    "column_names": ["user_id"],
                    "name": "email_addresses_user_id_key",
                    "comment": None,
                },
            ],
        },
        table_comment={
            ("public", "users"): {"text": None},
            ("public", "profiles"): {"text": None},
            ("public", "orders"): {"text": None},
            ("public", "order_items"): {"text": None},
            ("public", "products"): {"text": None},
            ("public", "product_categories"): {"text": None},
            ("public", "categories"): {"text": None},
            ("public", "courses"): {"text": None},
            ("public", "instructors"): {"text": None},
            ("public", "students"): {"text": None},
            ("public", "student_course_instructors"): {"text": None},
            ("public", "email_addresses"): {"text": None},
        },
        check_constraints={},
        table_options={},
        unreflectable={},
    )


@pytest.fixture
def sorted_tables():
    return [
        ("categories", []),
        ("products", []),
        ("users", []),
        ("orders", [("orders", "fk_user_order")]),
        (
            "product_categories",
            [
                ("product_categories", "fk_category"),
                ("product_categories", "fk_product_category"),
            ],
        ),
        ("profiles", [("profiles", "fk_user")]),
        ("order_items", [("order_items", "fk_product"), ("order_items", "fk_order")]),
        (None, []),
    ]


@pytest.fixture
def relationship_sorted_tables():
    return [
        ("categories", []),
        ("products", []),
        ("users", []),
        (
            "email_addresses",
            [
                ("email_addresses", "fk_user_email_address"),
            ],
        ),
        ("orders", [("orders", "fk_user_order")]),
        (
            "product_categories",
            [
                ("product_categories", "fk_category"),
                ("product_categories", "fk_product_category"),
            ],
        ),
        ("profiles", [("profiles", "fk_user")]),
        ("order_items", [("order_items", "fk_product"), ("order_items", "fk_order")]),
        ("students", []),
        ("courses", []),
        ("instructors", []),
        (
            "student_course_instructors",
            [
                ("student_course_instructors", "fk_student"),
                ("student_course_instructors", "fk_course"),
                ("student_course_instructors", "fk_instructor"),
            ],
        ),
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


Category = Table('categories', metadata,
    Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".categories_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=100), autoincrement=False, index=True, unique=True, nullable=False),

    PrimaryKeyConstraint('id', name='categories_pkey'),
    Index('category_name_idx', 'name'),
    UniqueConstraint('name', name='categories_name_key'),
    schema = 'public'
)


Product = Table('products', metadata,
    Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".products_id_seq\\'::regclass)'),
    Column('name', VARCHAR(length=255), autoincrement=False, nullable=False),
    Column('description', TEXT(), autoincrement=False, nullable=True),
    Column('price', NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False),
    Column('tags', ARRAY(TEXT()), autoincrement=False, nullable=True),

    PrimaryKeyConstraint('id', name='products_pkey'),
    CheckConstraint(sqltext='price >= 0::numeric', name='products_price_check'),
    schema = 'public'
)


User = Table('users', metadata,
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


Order = Table('orders', metadata,
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


ProductCategory = Table('product_categories', metadata,
    Column('product_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('category_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),

    PrimaryKeyConstraint('product_id', 'category_id', name='product_categories_pkey'),
    ForeignKeyConstraint(columns=['category_id'], refcolumns=['public.categories.id'], name='fk_category', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['product_id'], refcolumns=['public.products.id'], name='fk_product_category', ondelete='CASCADE'),
    schema = 'public'
)


Profile = Table('profiles', metadata,
    Column('user_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('bio', TEXT(), autoincrement=False, nullable=True),
    Column('website', VARCHAR(length=255), autoincrement=False, nullable=True),

    PrimaryKeyConstraint('user_id', name='profiles_pkey'),
    ForeignKeyConstraint(columns=['user_id'], refcolumns=['public.users.id'], name='fk_user', ondelete='CASCADE'),
    schema = 'public'
)


OrderItem = Table('order_items', metadata,
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


class OrderItem(Base):
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

    order: Mapped['Order'] = relationship(back_populates='order_items')
    product: Mapped['Product'] = relationship(back_populates='order_items')


class Profile(Base):
    __tablename__ = 'profiles'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='profiles_pkey'),
        ForeignKeyConstraint(columns=['user_id'], refcolumns=['public.users.id'], name='fk_user', ondelete='CASCADE'),
        {'schema': 'public'}
    )

    user_id: Mapped[int] = mapped_column('user_id', INTEGER(), nullable=False, primary_key=True, autoincrement=False)
    bio: Mapped[Optional[str]] = mapped_column('bio', TEXT(), nullable=True, autoincrement=False)
    website: Mapped[Optional[str]] = mapped_column('website', VARCHAR(length=255), nullable=True, autoincrement=False)

    user: Mapped['User'] = relationship(back_populates='profile')


ProductCategory = Table('product_categories', Base.metadata,
    Column('product_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),
    Column('category_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True),

    PrimaryKeyConstraint('product_id', 'category_id', name='product_categories_pkey'),
    ForeignKeyConstraint(columns=['category_id'], refcolumns=['public.categories.id'], name='fk_category', ondelete='CASCADE'),
    ForeignKeyConstraint(columns=['product_id'], refcolumns=['public.products.id'], name='fk_product_category', ondelete='CASCADE'),
    schema = 'public'
)


class Order(Base):
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

    order_items: Mapped[List['OrderItem']] = relationship(back_populates='order')
    user: Mapped['User'] = relationship(back_populates='orders')


class User(Base):
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

    orders: Mapped[List['Order']] = relationship(back_populates='user')
    profile: Mapped['Profile'] = relationship(back_populates='user')


class Product(Base):
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

    order_items: Mapped[List['OrderItem']] = relationship(back_populates='product')
    categories: Mapped[List['Category']] = relationship(secondary=ProductCategory, back_populates='products')


class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='categories_pkey'),
        Index('category_name_idx', 'name'),
        UniqueConstraint('name', name='categories_name_key'),
        {'schema': 'public'}
    )

    id: Mapped[int] = mapped_column('id', INTEGER(), nullable=False, primary_key=True, autoincrement=True, server_default='nextval(\\'"public".categories_id_seq\\'::regclass)')
    name: Mapped[str] = mapped_column('name', VARCHAR(length=100), nullable=False, autoincrement=False, index=True, unique=True)

    products: Mapped[List['Product']] = relationship(secondary=ProductCategory, back_populates='categories')"""


@pytest.fixture(scope="session")
def sqlmodel_tables():
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
    PrimaryKeyConstraint,
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


class OrderItem(SQLModel, table=True):
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

    order: 'Order' = Relationship(back_populates='order_items')
    product: 'Product' = Relationship(back_populates='order_items')


class Profile(SQLModel, table=True):
    __tablename__ = 'profiles'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='profiles_pkey'),
        ForeignKeyConstraint(columns=['user_id'], refcolumns=['public.users.id'], name='fk_user', ondelete='CASCADE'),
        {'schema': 'public'}
    )

    user_id: Optional[int] = Field(default=None, sa_column=Column('user_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True))
    bio: Optional[str] = Field(default=None, sa_column=Column('bio', TEXT(), autoincrement=False, nullable=True))
    website: Optional[str] = Field(default=None, sa_column=Column('website', VARCHAR(length=255), autoincrement=False, nullable=True))

    user: 'User' = Relationship(back_populates='profile')


class ProductCategory(SQLModel, table=True):
    __tablename__ = 'product_categories'
    __table_args__ = (
        PrimaryKeyConstraint('product_id', 'category_id', name='product_categories_pkey'),
        ForeignKeyConstraint(columns=['category_id'], refcolumns=['public.categories.id'], name='fk_category', ondelete='CASCADE'),
        ForeignKeyConstraint(columns=['product_id'], refcolumns=['public.products.id'], name='fk_product_category', ondelete='CASCADE'),
        {'schema': 'public'}
    )

    product_id: Optional[int] = Field(default=None, sa_column=Column('product_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True))
    category_id: Optional[int] = Field(default=None, sa_column=Column('category_id', INTEGER(), autoincrement=False, nullable=False, primary_key=True))


class Order(SQLModel, table=True):
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

    order_items: List['OrderItem'] = Relationship(back_populates='order')
    user: 'User' = Relationship(back_populates='orders')


class User(SQLModel, table=True):
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

    orders: List['Order'] = Relationship(back_populates='user')
    profile: 'Profile' = Relationship(back_populates='user')


class Product(SQLModel, table=True):
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

    order_items: List['OrderItem'] = Relationship(back_populates='product')
    categories: List['Category'] = Relationship(back_populates='products', link_model=ProductCategory)


class Category(SQLModel, table=True):
    __tablename__ = 'categories'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='categories_pkey'),
        Index('category_name_idx', 'name'),
        UniqueConstraint('name', name='categories_name_key'),
        {'schema': 'public'}
    )

    id: Optional[int] = Field(default=None, sa_column=Column('id', INTEGER(), autoincrement=True, nullable=False, primary_key=True, server_default='nextval(\\'"public".categories_id_seq\\'::regclass)'))
    name: str = Field(sa_column=Column('name', VARCHAR(length=100), autoincrement=False, index=True, unique=True, nullable=False))

    products: List['Product'] = Relationship(back_populates='categories', link_model=ProductCategory)"""
