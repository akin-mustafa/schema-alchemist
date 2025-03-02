import pytest
from sqlalchemy import (
    INTEGER,
    NUMERIC,
    DOUBLE_PRECISION,
    DATE,
    TEXT,
    TIMESTAMP,
    VARCHAR,
)
from sqlalchemy.dialects.postgresql import ENUM

from schema_alchemist.generators import SQLModelColumnGenerator
from schema_alchemist.utils import make_in_file_obj


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
            "    id: int = Field(sa_column=Column('id', INTEGER(), autoincrement=True, "
            "nullable=False, "
            "server_default='nextval(\\'\"public\".addresses_id_seq\\'::regclass)'))",
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
            "    user_id: int = Field(sa_column=Column('user_id', INTEGER(), "
            "autoincrement=False, nullable=False))",
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
            "    address_line1: str = Field(sa_column=Column('address_line1', "
            "VARCHAR(length=200), autoincrement=False, nullable=False))",
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
            "    created_at: datetime = Field(sa_column=Column('created_at', "
            "TIMESTAMP(), autoincrement=False, nullable=False, "
            "server_default='CURRENT_TIMESTAMP'))",
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
            "    description: Optional[str] = Field(default=None, sa_column=Column('description', "
            "TEXT(), autoincrement=False, nullable=True))",
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
            "    order_date: Optional[date] = Field(default=None, sa_column=Column('order_date', "
            "DATE(), autoincrement=False, nullable=True, server_default='CURRENT_DATE'))",
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
            "    status: order_status_enum = Field(sa_column=Column('status', "
            "ENUM('pending', 'processed', 'shipped', 'delivered', 'cancelled', "
            "name='order_status_enum'), autoincrement=False, nullable=False, "
            "server_default=\"'pending'::order_status_enum\"))",
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
            "    total_amount: Decimal = Field(sa_column=Column('total_amount', "
            "NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))",
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
            "    unit_price: float = Field(sa_column=Column('unit_price', "
            "DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))",
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
            "    total_price: Optional[Decimal] = Field(default=None, sa_column=Column('total_price', "
            "NUMERIC(precision=10, scale=2), "
            "Computed(sqltext='((quantity)::numeric * unit_price)', persisted=True), "
            "autoincrement=False, nullable=True))",
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
            "    id: int = Field(sa_column=Column('id', INTEGER(), Identity(start=1, "
            "increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), "
            "autoincrement=True, nullable=False))",
        ),
    ),
)
def test_sqlmodel_column_generate(pre_configured_ipr, input_value, expected):
    pre_configured_ipr.insert(make_in_file_obj("order_status_enum"))
    column_generator = SQLModelColumnGenerator(
        input_value, pre_configured_ipr, "TestTable"
    )
    result = column_generator.generate()
    assert result == expected
