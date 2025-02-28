from datetime import datetime, date
from decimal import Decimal
from typing import List, Tuple, Dict, Optional, DefaultDict, FrozenSet, Set
from unittest.mock import patch

import pytest
from sqlalchemy import (
    Table,
    ARRAY,
    VARCHAR,
    INTEGER,
    Column,
    Computed,
    TEXT,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
    CheckConstraint,
    ForeignKeyConstraint,
    Identity,
    ForeignKey,
    NUMERIC,
    TIMESTAMP,
    DATE,
    DOUBLE_PRECISION,
)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.testing.engines import mock_engine
from sqlmodel import SQLModel, Field, Relationship

from schema_alchemist.utils import ImportPathResolver


@pytest.fixture
def import_path_resolver():
    return ImportPathResolver()


@pytest.fixture
def pre_configured_ipr():
    ipr = ImportPathResolver()
    ipr.insert_many(
        Table,
        DATE,
        DOUBLE_PRECISION,
        TIMESTAMP,
        NUMERIC,
        ENUM,
        ARRAY,
        VARCHAR,
        INTEGER,
        Column,
        Computed,
        TEXT,
        Index,
        Identity,
        PrimaryKeyConstraint,
        ForeignKeyConstraint,
        ForeignKey,
        UniqueConstraint,
        mapped_column,
        Mapped,
        CheckConstraint,
        SQLModel,
        Field,
        List,
        Tuple,
        Dict,
        Optional,
        Decimal,
        DefaultDict,
        Set,
        FrozenSet,
        Relationship,
        datetime,
        date,
        relationship,
    )
    return ipr


@pytest.fixture
def engine():
    return mock_engine("postgresql")


@pytest.fixture
def inspector(engine):
    with patch("sqlalchemy.Inspector") as mock_inspector:
        yield mock_inspector(engine)
