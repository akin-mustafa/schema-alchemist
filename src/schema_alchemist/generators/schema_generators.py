from collections import defaultdict
from functools import cached_property
from typing import (
    Optional,
    List,
    Type,
    Tuple,
)

from sqlalchemy import (
    Enum as SQLAlchemyEnum,
    Table,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    UniqueConstraint,
    CheckConstraint,
    PrimaryKeyConstraint,
    Computed,
    Identity,
    MetaData,
)
from sqlalchemy.engine.reflection import _ReflectionInfo
from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped,
    relationship,
)
from sqlmodel import SQLModel, Field, Relationship

from schema_alchemist.constants import SchemaTypeEnum, SQLRelationshipType
from schema_alchemist.generators import (
    DeclarativeTableGenerator,
    EnumGenerator,
    SQLModelTableGenerator,
    TableGenerator,
)
from schema_alchemist.utils import (
    ImportPathResolver,
    convert_to_class_name,
    inflect_engine,
    to_camel_case,
    to_snake_case,
    make_in_file_obj,
    resolve_column_type,
)


class CoreSchemaGenerator:
    def __init__(
        self,
        reflected_data: _ReflectionInfo,
        sorted_tables_and_fks: List[Tuple[str, List[Tuple[str, str]]]],
        schema: Optional[str] = None,
        add_comments: bool = False,
        create_table_args: bool = False,
        use_camel_case: bool = False,
        use_generic_types: bool = False,
    ):
        self.reflected_data = reflected_data
        self.sorted_tables_and_fks = sorted_tables_and_fks
        self.schema = schema
        self.create_table_args = create_table_args
        self.add_comments = add_comments
        self.use_camel_case = use_camel_case
        self.use_generic_types = use_generic_types

        self.import_path_resolver = ImportPathResolver()

        self.tables = list(self.reflected_data.columns.keys())
        self.table_class_name_map = {
            table: convert_to_class_name(inflect_engine.to_singular(table[1]))
            for table in self.sorted_tables
        }

        self.enum_names = []

    @cached_property
    def sorted_tables(self) -> List[Tuple[Optional[str], str]]:
        sorted_tables = [
            (self.schema, t[0]) for t in self.sorted_tables_and_fks if t[0] is not None
        ]
        views = list(set(self.tables) - set(sorted_tables))
        return sorted_tables + views

    @property
    def metadata_name(self) -> str:
        return self.find_unique_name("metadata")

    def find_unique_name(self, name: str) -> str:
        table_names = list(self.table_class_name_map.values())
        while True:
            if name not in table_names and name not in self.enum_names:
                break
            name += "_"
        return name

    @property
    def schema_type_imports(self):
        return Table, Column, MetaData

    def collect_imports(self):
        meta = make_in_file_obj(self.metadata_name)
        imports = {
            meta,
            *self.schema_type_imports,
        }

        indexes = [
            index
            for indexes in self.reflected_data.indexes.values()
            for index in indexes
            if not index.get("duplicates_constraint")
        ]
        if indexes and any(indexes):
            imports.add(Index)

        checks = [check for check in self.reflected_data.check_constraints.values()]
        if checks and any(checks):
            imports.add(CheckConstraint)

        unique_indexes = [
            index for index in self.reflected_data.unique_constraints.values()
        ]
        if unique_indexes and any(unique_indexes):
            imports.add(UniqueConstraint)

        pks = [pk for pk in self.reflected_data.pk_constraint.values()]
        if pks and any(pks):
            imports.add(PrimaryKeyConstraint)

        fks = [fk for fk in self.reflected_data.foreign_keys.values()]
        if fks and any(fks):
            imports.update([ForeignKey, ForeignKeyConstraint])

        for table in self.sorted_tables:
            table_class_name = self.table_class_name_map[table]
            imports.add(make_in_file_obj(table_class_name))
            for column in self.reflected_data.columns[table]:
                column_type = resolve_column_type(column, table_class_name)

                if column["nullable"]:
                    imports.add(Optional)

                if column.get("computed"):
                    imports.add(Computed)

                if column.get("identity"):
                    imports.add(Identity)

                imports.update(column_type.sql_types)
                imports.update(column_type.python_types)

                if self.use_generic_types:
                    imports.update(column_type.sql_generic_types)

        self.import_path_resolver.insert_many(*imports)

    def generate_base_definition(self) -> str:
        usage = self.import_path_resolver.get_usage_name(MetaData)
        return f"{self.metadata_name} = {usage}(schema={self.schema!r})"

    def generate_imports(self):
        return "\n".join(self.import_path_resolver.build_all_import_statements())

    def generate(self) -> str:
        self.collect_imports()
        tables_generators = [
            TableGenerator(
                name=table[1],
                import_path_resolver=self.import_path_resolver,
                schema=self.schema,
                metadata_name=self.metadata_name,
                columns=self.reflected_data.columns[table],
                comment=self.reflected_data.table_comment[table],
                check_constraints=self.reflected_data.check_constraints[table],
                foreign_keys=self.reflected_data.foreign_keys[table],
                indexes=self.reflected_data.indexes[table],
                primary_key=self.reflected_data.pk_constraint[table],
                unique_constraints=self.reflected_data.unique_constraints[table],
            )
            for table in self.sorted_tables
        ]

        import_statements = self.generate_imports()

        metadata = self.generate_base_definition()

        tables = [tg.generate() for tg in tables_generators]
        return "\n\n\n".join([import_statements, metadata, *tables])


class DeclarativeSchemaGenerator(CoreSchemaGenerator):
    def __init__(
        self,
        reflected_data: _ReflectionInfo,
        sorted_tables_and_fks: List[Tuple[str, List[Tuple[str, str]]]],
        schema: Optional[str] = None,
        add_comments: bool = False,
        create_table_args: bool = False,
        use_camel_case: bool = False,
    ):
        super().__init__(
            reflected_data,
            sorted_tables_and_fks,
            schema,
            add_comments,
            create_table_args,
            use_camel_case,
        )
        self.relationships = defaultdict(list)
        self.relation_names_map = defaultdict(list)
        self.table_column_map = defaultdict(set)
        self.m2m_associated_tables = []

        self.table_class_name_map = {
            table: convert_to_class_name(inflect_engine.to_singular(table[1]))
            for table in self.sorted_tables
        }

        self.table_pk_map = {
            table: pk_data["constrained_columns"]
            for table, pk_data in self.reflected_data.pk_constraint.items()
        }

        self.table_unique_cols_map = defaultdict(list)
        for table, values in self.reflected_data.unique_constraints.items():
            for value in values:
                self.table_unique_cols_map[table].append(value["column_names"])

        self.nullable_column_map = defaultdict(set)
        self.enums = []
        self.columns_types = set()

        for table, columns in self.reflected_data.columns.items():
            for column in columns:
                column_name = column["name"]
                column_type = column["type"]

                self.table_column_map[table].add(column_name)

                if column["nullable"]:
                    self.nullable_column_map[table].add(column_name)

                if isinstance(column_type, SQLAlchemyEnum):
                    table_class = self.table_class_name_map[table]
                    name = column_type.name or f"{table_class}{column_name}"
                    members = column_type.enums
                    self.enums.append((name, members))

                self.columns_types.add(column_type)

    @property
    def metadata_name(self) -> str:
        return self.find_unique_name("Base")

    @property
    def schema_type_imports(self):
        return DeclarativeBase, Mapped, mapped_column, relationship, Column, Table

    def resolve_m2m_relationship(self, table, fks):
        if not fks:
            return None

        pk_columns = set(self.table_pk_map[table])
        column_names = self.table_column_map[table]
        fk_columns = set()
        target_tables = set()
        for fk in fks:
            fk_columns.update({col for col in fk["constrained_columns"]})
            target_tables.add((fk["referred_schema"], fk["referred_table"]))

        if fk_columns == column_names:
            return target_tables

        non_pk_columns = column_names - pk_columns
        if non_pk_columns == fk_columns:
            return target_tables

        return None

    def resolve_relationship_type_of_fk(self, table, fk):
        fk_columns = fk["constrained_columns"]

        if (
            fk_columns in self.table_unique_cols_map[table]
            or fk_columns == self.table_pk_map[table]
        ):
            return SQLRelationshipType.o2o

        return SQLRelationshipType.o2m

    @property
    def singular_suffixes(self) -> List[str]:
        if self.use_camel_case:
            return ["Detail", "Instance", "Data"]
        return ["_detail", "_instance", "_data"]

    @property
    def plural_suffixes(self) -> List[str]:
        if self.use_camel_case:
            return ["Set", "List", "Data"]
        return ["_set", "_list", "_data"]

    def get_suffixes(self, singular: bool = True) -> List[str]:
        if singular:
            return self.singular_suffixes
        return self.plural_suffixes

    def table_has_attribute(self, attribute, table):
        columns = self.table_column_map[table]
        relationships = self.relation_names_map[table]
        return attribute in columns or attribute in relationships

    def find_unique_key_for_relation_attribute(
        self,
        attribute_name,
        main_tabel,
        target_table,
        use_singular_suffixes,
    ) -> str:

        if self.table_has_attribute(attribute_name, main_tabel):
            suffixes = self.get_suffixes(use_singular_suffixes)
            attr_name_singular = inflect_engine.to_singular(attribute_name)
            new_name = None

            for suffix in suffixes:
                tmp_attribute_name = f"{attr_name_singular}{suffix}"

                if not self.table_has_attribute(tmp_attribute_name, main_tabel):
                    new_name = tmp_attribute_name
                    break

            # raise error if no attribute name found
            if new_name is None:
                raise ValueError(
                    "No suitable relationship attribute "
                    "name found for {} in Table: {}".format(
                        target_table[1], main_tabel[1]
                    )
                )

            return new_name

        return attribute_name

    def convert_to_relation_attribute_name(
        self, main_tabel, target_table, relation_type
    ):
        attribute_name = inflect_engine.to_singular(target_table[1].lower())
        use_singular_suffixes = True

        if relation_type in (SQLRelationshipType.m2o, SQLRelationshipType.m2m):
            use_singular_suffixes = False
            attribute_name = inflect_engine.to_plural(attribute_name)

        attribute_name = self.find_unique_key_for_relation_attribute(
            attribute_name,
            main_tabel,
            target_table,
            use_singular_suffixes,
        )

        if self.use_camel_case:
            return to_camel_case(attribute_name)

        return to_snake_case(attribute_name)

    def resolve_relation_and_back_populates_names(
        self, main_table, target_table, relation_type: SQLRelationshipType
    ) -> Tuple[str, str]:

        attribute_name = self.convert_to_relation_attribute_name(
            main_table, target_table, relation_type
        )

        back_populates = self.convert_to_relation_attribute_name(
            target_table, main_table, relation_type.reversed_relationship
        )

        return attribute_name, back_populates

    def create_relationship_metadata(
        self,
        main_table: Tuple[Optional[str], str],
        target_table: Tuple[Optional[str], str],
        relation_type: SQLRelationshipType,
        nullable: bool = False,
        secondary_table: Optional[str] = None,
    ):
        main_class = self.table_class_name_map[main_table]
        target_class = self.table_class_name_map[target_table]
        attribute_name, back_populates = self.resolve_relation_and_back_populates_names(
            main_table, target_table, relation_type
        )

        relationship_data = {
            "attribute_name": attribute_name,
            "target_class": target_class,
            "back_populates": back_populates,
            "relation_type": relation_type,
            "nullable": nullable,
            "secondary_table": secondary_table,
        }
        reverse_relation_data = {
            "attribute_name": back_populates,
            "target_class": main_class,
            "back_populates": attribute_name,
            "relation_type": relation_type.reversed_relationship,
            "nullable": nullable,
            "secondary_table": secondary_table,
        }
        if relationship_data not in self.relationships[main_table]:
            self.relationships[main_table].append(relationship_data)

        if reverse_relation_data not in self.relationships[target_table]:
            self.relationships[target_table].append(reverse_relation_data)

    def handle_m2m_relations(self, secondary_table, tables):
        secondary_class = self.table_class_name_map[secondary_table]
        for table in sorted(tables, key=lambda t: t[1]):
            target_tables = tables - {table}
            for target_table in sorted(target_tables, key=lambda t: t[1]):
                self.create_relationship_metadata(
                    table,
                    target_table,
                    SQLRelationshipType.m2m,
                    nullable=False,
                    secondary_table=secondary_class,
                )

    def resolve_relationships(self):

        for main_table, fks in self.reflected_data.foreign_keys.items():
            target_tables = self.resolve_m2m_relationship(main_table, fks)

            if target_tables:
                self.m2m_associated_tables.append(main_table)
                self.handle_m2m_relations(main_table, target_tables)
                continue

            for fk in fks:
                target_table = (fk["referred_schema"], fk["referred_table"])
                relation_type = self.resolve_relationship_type_of_fk(main_table, fk)

                fk_columns = fk["constrained_columns"]
                nullable = set(fk_columns).issubset(
                    set(self.nullable_column_map[main_table])
                )

                self.create_relationship_metadata(
                    main_table,
                    target_table,
                    relation_type,
                    nullable,
                    None,
                )

    def generate_base_definition(self) -> str:
        declarative_class = self.import_path_resolver.get_usage_name(DeclarativeBase)
        return f"class {self.metadata_name}({declarative_class}):\n    pass"

    def generate_enums(self):
        return [
            EnumGenerator(name, items, self.import_path_resolver).generate()
            for name, items in self.enums
        ]

    def generate(self) -> str:
        self.collect_imports()
        columns = self.reflected_data.columns
        table_comment = self.reflected_data.table_comment
        check_constraints = self.reflected_data.check_constraints
        foreign_keys = self.reflected_data.foreign_keys
        indexes = self.reflected_data.indexes
        pk_constraint = self.reflected_data.pk_constraint
        unique_constraints = self.reflected_data.unique_constraints

        self.resolve_relationships()

        enums = self.generate_enums()

        tables_generators = []
        for table in reversed(self.sorted_tables):
            if table in self.m2m_associated_tables:
                tables_generators.append(
                    TableGenerator(
                        name=table[1],
                        import_path_resolver=self.import_path_resolver,
                        schema=self.schema,
                        metadata_name=f"{self.metadata_name}.metadata",
                        columns=columns[table],
                        comment=table_comment[table],
                        check_constraints=check_constraints[table],
                        foreign_keys=foreign_keys[table],
                        indexes=indexes[table],
                        primary_key=pk_constraint[table],
                        unique_constraints=unique_constraints[table],
                    )
                )

            else:
                generator = DeclarativeTableGenerator(
                    name=table[1],
                    import_path_resolver=self.import_path_resolver,
                    schema=self.schema,
                    metadata_name=self.metadata_name,
                    columns=columns[table],
                    comment=table_comment[table],
                    check_constraints=check_constraints[table],
                    foreign_keys=foreign_keys[table],
                    indexes=indexes[table],
                    primary_key=pk_constraint[table],
                    unique_constraints=unique_constraints[table],
                    relationships=self.relationships[table],
                )
                tables_generators.append(generator)

        import_statements = self.generate_imports()

        tables = [tg.generate() for tg in tables_generators]
        return "\n\n\n".join(
            [import_statements, *enums, self.generate_base_definition(), *tables]
        )


class SQLModelSchemaGenerator(DeclarativeSchemaGenerator):

    @cached_property
    def schema_type_imports(self):
        return SQLModel, Field, Relationship, Column

    def generate_base_definition(self) -> str:
        return ""

    def generate(self):
        self.collect_imports()
        self.resolve_relationships()
        enums = self.generate_enums()
        tables_generators = [
            SQLModelTableGenerator(
                name=table[1],
                import_path_resolver=self.import_path_resolver,
                schema=self.schema,
                metadata_name=self.metadata_name,
                columns=self.reflected_data.columns[table],
                comment=self.reflected_data.table_comment[table],
                check_constraints=self.reflected_data.check_constraints[table],
                foreign_keys=self.reflected_data.foreign_keys[table],
                indexes=self.reflected_data.indexes[table],
                primary_key=self.reflected_data.pk_constraint[table],
                unique_constraints=self.reflected_data.unique_constraints[table],
                relationships=self.relationships[table],
            )
            for table in reversed(self.sorted_tables)
        ]

        import_statements = self.generate_imports()
        tables = [tg.generate() for tg in tables_generators]
        return "\n\n\n".join([import_statements, *enums, *tables])


class SchemaGeneratorFactory:
    def __init__(
        self,
        reflected_data: _ReflectionInfo,
        sorted_tables_and_fks: List[Tuple[str, List[Tuple[str, str]]]],
        schema_type: SchemaTypeEnum = SchemaTypeEnum.table,
        schema: Optional[str] = None,
        add_comments: bool = False,
        create_table_args: bool = False,
        use_camel_case: bool = False,
    ):
        self.reflected_data = reflected_data
        self.sorted_tables_and_fks = sorted_tables_and_fks
        self.schema = schema
        self.add_comments = add_comments
        self.create_table_args = create_table_args
        self.use_camel_case = use_camel_case
        self.schema_type = schema_type

    def get_generator_class(self) -> Type[CoreSchemaGenerator]:
        if self.schema_type == SchemaTypeEnum.declarative:
            return DeclarativeSchemaGenerator
        if self.schema_type == SchemaTypeEnum.sqlmodel:
            return SQLModelSchemaGenerator
        if self.schema_type == SchemaTypeEnum.table:
            return CoreSchemaGenerator
        raise ValueError(f"Unknown schema type: {self.schema_type}")

    def generate(self) -> str:
        generator_class = self.get_generator_class()

        generator = generator_class(
            self.reflected_data,
            self.sorted_tables_and_fks,
            self.schema,
            self.add_comments,
            self.create_table_args,
            self.use_camel_case,
        )
        return generator.generate()
