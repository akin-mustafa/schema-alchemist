import pytest
from sqlalchemy import INTEGER, VARCHAR, TEXT, ARRAY
from sqlalchemy.dialects.mysql import ENUM

from schema_alchemist.generators import SQLModelTableGenerator

UserTable = """class User(Base, table=True):
    __tablename__ = 'user'
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
    role: user_role = Field(sa_column=Column('role', ENUM('admin', 'user', 'guest'), autoincrement=False, nullable=False, server_default="'user'::user_role"))
    phone_numbers: Optional[List] = Field(default=None, sa_column=Column('phone_numbers', ARRAY(TEXT()), autoincrement=False, nullable=True))"""


@pytest.mark.parametrize(
    "name, schema, columns, comment, check_constraints, foreign_keys, indexes, "
    "primary_key, unique_constraints, expected",
    (
        (
            "user",
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
def test_sql_model_table_generator(
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
    pre_configured_ipr.insert("__file__.user_role")
    generator = SQLModelTableGenerator(
        name,
        "Base",
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
