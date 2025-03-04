from copy import deepcopy
from functools import cached_property
from typing import (
    Optional,
    List,
    Any,
    Dict,
    Set,
)

from sqlalchemy import (
    CheckConstraint,
    ForeignKeyConstraint,
    Index,
    PrimaryKeyConstraint,
    Table,
    UniqueConstraint,
)

from schema_alchemist.generators.base_generators import BaseGenerator
from schema_alchemist.generators.column_generators import (
    ColumnGenerator,
    DeclarativeColumnGenerator,
    SQLModelColumnGenerator,
)
from schema_alchemist.generators.relationship_generators import (
    DeclarativeRelationGenerator,
    SQLModelRelationGenerator,
)
from schema_alchemist.utils import (
    ImportPathResolver,
    convert_to_class_name,
)


class TableGenerator(BaseGenerator):
    """
    Example generated code:

        MyTable = Table("my_table", metadata,
            Column("id", Integer, primary_key=True),
            ...,
            schema="public",
            ...
        )
    """

    klass = Table
    column_generator = ColumnGenerator

    def __init__(
        self,
        name: str,
        metadata_name: str,
        import_path_resolver: ImportPathResolver,
        schema: Optional[str] = None,
        columns: Optional[List[Dict[str, Any]]] = None,
        comment: Optional[Dict[str, Optional[str]]] = None,
        check_constraints: Optional[List[Dict[str, Any]]] = None,
        foreign_keys: Optional[List[Dict[str, Any]]] = None,
        indexes: Optional[List[Dict[str, Any]]] = None,
        primary_key: Optional[Dict[str, Any]] = None,
        unique_constraints: Optional[List[Dict[str, Any]]] = None,
        relationships: Optional[List[Dict[str, Any]]] = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.metadata_name = metadata_name
        self.schema = schema
        self.columns = columns or []
        self.comment = comment
        self.check_constraints = check_constraints
        self.foreign_keys = foreign_keys
        self.indexes = indexes
        self.primary_key = primary_key
        self.unique_constraints = unique_constraints
        self.relationships = relationships
        super().__init__(import_path_resolver, *args, **kwargs)

    def create_fk_constraint(self, foreign_key: Dict[str, Any]) -> str:
        target_table = foreign_key["referred_table"]
        referred_columns = [
            (
                f"{self.schema}.{target_table}.{col}"
                if self.schema
                else f"{target_table}.{col}"
            )
            for col in foreign_key["referred_columns"]
        ]
        columns = foreign_key["constrained_columns"]
        name = foreign_key["name"]
        comment = foreign_key.get("comment")
        parameters = {
            "columns": columns,
            "refcolumns": referred_columns,
            "name": name,
            "comment": comment,
            **foreign_key["options"],
        }
        return self.generate_function_definition(ForeignKeyConstraint, parameters)

    def create_index_constraint(self, parameters: Dict[str, Any]) -> str:
        parameters = deepcopy(parameters)
        parameters["expressions"] = parameters.pop("column_names")
        parameters["dialect_kw"] = parameters.pop("dialect_options", None)
        parameters.pop("include_columns", None)
        parameters.pop("duplicates_constraint", None)
        parameters.pop("dialect_kw", None)

        return self.generate_function_definition(Index, parameters)

    def create_check_constraint(self, parameters: Dict[str, Any]) -> str:
        return self.generate_function_definition(CheckConstraint, parameters)

    def create_pk_constraint(self, parameters: Dict[str, Any]) -> str:
        parameters = deepcopy(parameters)
        parameters["columns"] = parameters.pop("constrained_columns")
        return self.generate_function_definition(PrimaryKeyConstraint, parameters)

    def create_unique_constraint(self, parameters: Dict[str, Any]) -> str:
        parameters = deepcopy(parameters)
        parameters["columns"] = parameters.pop("column_names")
        return self.generate_function_definition(UniqueConstraint, parameters)

    def create_constraints(self) -> List[str]:
        constraints = []

        if self.primary_key:
            constraints.append(self.create_pk_constraint(self.primary_key))

        for fk in self.foreign_keys:
            constraints.append(self.create_fk_constraint(fk))

        for idx in self.indexes:
            if idx.get("duplicates_constraint"):
                continue
            constraints.append(self.create_index_constraint(idx))

        for uni in self.unique_constraints:
            constraints.append(self.create_unique_constraint(uni))

        for cc in self.check_constraints:
            constraints.append(self.create_check_constraint(cc))

        return constraints

    @cached_property
    def table_class_name(self):
        return convert_to_class_name(self.name)

    @cached_property
    def foreignkey_column(self) -> Dict[str, Dict[str, Any]]:
        return {
            fk["constrained_columns"][0]: fk
            for fk in self.foreign_keys
            if len(fk["constrained_columns"]) == 1
        }

    @cached_property
    def indexed_column(self) -> Set[str]:
        return {
            index["column_names"][0]
            for index in self.indexes
            if len(index["column_names"]) == 1 and not index["unique"]
        }

    @cached_property
    def unique_columns(self) -> Set[str]:
        return {
            index["column_names"][0]
            for index in self.unique_constraints
            if len(index["column_names"]) == 1
        }

    @cached_property
    def primary_key_columns(self) -> Set[str]:
        if not self.primary_key:
            return set()

        return set(self.primary_key["constrained_columns"])

    def enrich_column(self, column: dict[str, Any]):
        name = column["name"]
        column["index"] = name in self.indexed_column or None
        column["unique"] = name in self.unique_columns or None
        column["primary_key"] = name in self.primary_key_columns or False
        column["foreign_key"] = self.foreignkey_column.get(name)
        return column

    def generate_columns(self):
        return ",\n".join(
            [
                self.column_generator(
                    self.enrich_column(column),
                    self.import_path_resolver,
                    self.table_class_name,
                    indentation=self.indent,
                ).generate()
                for column in self.columns
            ]
        )

    def get_table_args_schema(self):
        return f"schema = '{self.schema}'"

    def create_table_args(self) -> str:
        """
        Returns string like:

            PrimaryKeyConstraint("id"),
            CheckConstraint("..."),
            schema="public"
        """

        table_args = self.create_constraints()

        if self.schema:
            table_args.append(self.get_table_args_schema())

        return ",\n".join([f"{self.indent}{con}" for con in table_args if con])

    def generate_table(self):
        parameters = [
            self.generate_columns(),
            self.create_table_args(),
        ]

        return ",\n\n".join(parameters)

    def generate(self):
        table_data = self.generate_table()
        name = self.import_path_resolver.get_usage_name(self.klass)
        return (
            f"{self.table_class_name} = {name}("
            f"'{self.name}', {self.metadata_name},\n{table_data}\n)"
        )


class DeclarativeTableGenerator(TableGenerator):
    """
    Generates a declarative-style class:

        class SomeTable(Base):
            __tablename__ = "some_table"
            __table_args__ = (PrimaryKeyConstraint("id"), ..., {"schema": "public"})

            id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
            ...

    Unlike the base TableGenerator, we won't emit Table(...) calls directly;
    instead, we produce a class definition using mapped_column(...).
    """

    column_generator = DeclarativeColumnGenerator
    relations_generator = DeclarativeRelationGenerator

    @property
    def plus_one_indent(self):
        return self.indent + self.default_indentation

    def create_table_definition(self):
        return [f"class {self.table_class_name}({self.metadata_name}):"]

    def generate_relationships(self) -> str:
        relationships = []
        for relation in self.relationships:
            rg = self.relations_generator(
                import_path_resolver=self.import_path_resolver,
                indentation=self.indentation,
                **relation,
            )
            relationships.append(rg.generate())

        return "\n".join(relationships)

    def generate_columns(self):
        return "\n".join(
            [
                self.column_generator(
                    self.enrich_column(column),
                    self.import_path_resolver,
                    self.table_class_name,
                    indentation=self.indent,
                ).generate()
                for column in self.columns
            ]
        )

    def generate(self) -> str:
        """
        Produce something like:

            class MyTableName(Base):
                __tablename__ = "my_table"
                __table_args__ = (PrimaryKeyConstraint("id"), ..., {"schema": "public"})

                id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
                ...
        """
        lines = self.create_table_definition()
        table_args = self._create_table_args()

        if table_args:
            lines.append(table_args)

        lines = ["\n".join(lines), self.generate_columns()]

        if self.relationships:
            lines.append(self.generate_relationships())

        return "\n\n".join(lines)

    def _create_table_args(self) -> str:
        """
        In standard SQLAlchemy declarative, __table_args__ can be a tuple of constraints
        plus an optional dictionary for extra arguments like 'schema'.
        E.g.:

            __table_args__ = (
                PrimaryKeyConstraint("id"),
                CheckConstraint("price > 0"),
                {"schema": "public"}
            )
        """
        lines = [f"{self.indent}__tablename__ = {self.name!r}"]

        constraint_list = self.create_constraints()

        extra_kwargs = {}
        if self.schema:
            extra_kwargs["schema"] = self.schema
        comment = self.comment.get("text")
        if comment:
            extra_kwargs["comment"] = comment

        items = []
        items.extend(constraint_list)
        if extra_kwargs:
            dict_str = ", ".join(f"{k!r}: {v!r}" for k, v in extra_kwargs.items())
            items.append(f"{{{dict_str}}}")
        join_pattern = f",\n{self.plus_one_indent}"

        table_args = join_pattern.join(items)

        lines.append(
            f"{self.indent}__table_args__ = "
            f"(\n{self.plus_one_indent}{table_args}\n{self.indent})"
        )

        return "\n".join(lines)


class SQLModelTableGenerator(DeclarativeTableGenerator):
    """
    Generates a SQLModel-based class, e.g.:

        class MyTable(SQLModel, table=True):
            __tablename__ = "my_table"
            __table_args__ = (
                PrimaryKeyConstraint("id"),
                {"schema": "public"}
            )

            id: int = Field(sa_column=Column("id", Integer, primary_key=True))
            name: Optional[str] = Field(sa_column=Column("name", String, nullable=True))
            ...
    """

    column_generator = SQLModelColumnGenerator
    relations_generator = SQLModelRelationGenerator

    def enrich_column(self, column: dict[str, Any]):
        super().enrich_column(column)
        name = column["name"]
        column["alias"] = name

        return column

    def create_table_definition(self):
        return [f"class {self.table_class_name}({self.metadata_name}, table=True):"]
