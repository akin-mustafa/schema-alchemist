from enum import Enum


class SchemaTypeEnum(str, Enum):
    table = "table"
    declarative = "declarative"
    sqlmodel = "sqlmodel"


class SQLRelationshipType(str, Enum):
    m2m = "m2m"
    m2o = "m2o"
    o2m = "o2m"
    o2o = "o2o"

    @property
    def reversed_relationship(self):
        if self == SQLRelationshipType.m2o:
            return SQLRelationshipType.o2m
        elif self == SQLRelationshipType.o2m:
            return SQLRelationshipType.m2o
        return self