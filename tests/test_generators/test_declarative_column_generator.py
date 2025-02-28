import pytest
from sqlalchemy import (
    INTEGER,
    VARCHAR,
    TIMESTAMP,
    TEXT,
    DATE,
    NUMERIC,
    DOUBLE_PRECISION,
)
from sqlalchemy.dialects.postgresql import ENUM

from schema_alchemist.generators import DeclarativeColumnGenerator
from schema_alchemist.utils import make_in_file_obj


@pytest.mark.parametrize(
    "data, annotation, mapped_column",
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
            "int",
            (
                "    id: Mapped[int] = mapped_column('id', INTEGER(), nullable=False, "
                "autoincrement=True, server_default='nextval("
                "\\'\"public\".addresses_id_seq\\'::regclass)')"
            ),
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
            "int",
            (
                "    user_id: Mapped[int] = mapped_column('user_id', INTEGER(), "
                "nullable=False, autoincrement=False)"
            ),
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
            "str",
            (
                "    address_line1: Mapped[str] = mapped_column('address_line1', "
                "VARCHAR(length=200), nullable=False, autoincrement=False)"
            ),
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
            "datetime",
            (
                "    created_at: Mapped[datetime] = mapped_column('created_at', "
                "TIMESTAMP(), nullable=False, autoincrement=False, "
                "server_default='CURRENT_TIMESTAMP')"
            ),
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
            "Optional[str]",
            (
                "    description: Mapped[Optional[str]] = mapped_column('description', "
                "TEXT(), nullable=True, autoincrement=False)"
            ),
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
            "Optional[date]",
            (
                "    order_date: Mapped[Optional[date]] = mapped_column('order_date', "
                "DATE(), nullable=True, autoincrement=False, "
                "server_default='CURRENT_DATE')"
            ),
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
            "order_status_enum",
            (
                "    status: Mapped[order_status_enum] = mapped_column('status', "
                "ENUM('pending', 'processed', 'shipped', 'delivered', 'cancelled', "
                "name='order_status_enum'), nullable=False, autoincrement=False, "
                "server_default=\"'pending'::order_status_enum\")"
            ),
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
            "Decimal",
            (
                "    total_amount: Mapped[Decimal] = mapped_column('total_amount', "
                "NUMERIC(precision=10, scale=2), nullable=False, autoincrement=False)"
            ),
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
            "float",
            (
                "    unit_price: Mapped[float] = mapped_column('unit_price', "
                "DOUBLE_PRECISION(precision=53), nullable=False, autoincrement=False)"
            ),
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
            "Optional[Decimal]",
            (
                "    total_price: Mapped[Optional[Decimal]] = mapped_column("
                "'total_price', NUMERIC(precision=10, scale=2), "
                "Computed(sqltext='((quantity)::numeric * unit_price)', persisted=True), "
                "nullable=True, autoincrement=False)"
            ),
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
            "int",
            (
                "    id: Mapped[int] = mapped_column('id', INTEGER(), Identity(start=1, "
                "increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), "
                "nullable=False, autoincrement=True)"
            ),
        ),
    ),
)
def test_declarative_column_generation(
    data, annotation, mapped_column, pre_configured_ipr
):
    pre_configured_ipr.insert(make_in_file_obj("order_status_enum"))
    generator = DeclarativeColumnGenerator(data, pre_configured_ipr, "TestTable")

    assert generator.python_annotation == annotation
    assert generator.generate() == mapped_column
