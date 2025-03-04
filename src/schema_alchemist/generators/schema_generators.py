import logging
from collections import defaultdict
from functools import cached_property
from typing import (
    Optional,
    List,
    Type,
    Tuple,
    Dict,
    Any,
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
    registry,
)
from sqlmodel import SQLModel, Field, Relationship

from schema_alchemist.constants import SQLRelationshipType
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
    StringReprWrapper,
)

logger = logging.getLogger(__name__)


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
        excluded_relationship_tables: Optional[List[Tuple[Optional[str], str]]] = None,
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
        self.excluded_relationship_tables = [
            (self.schema, table) for table in excluded_relationship_tables or []
        ]

        self.table_class_name_map = {
            table: convert_to_class_name(table[1]) for table in self.sorted_tables
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

                if column.get("nullable"):
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
                comment=self.reflected_data.table_comment.get(table, {}),
                check_constraints=self.reflected_data.check_constraints.get(table, []),
                foreign_keys=self.reflected_data.foreign_keys.get(table, []),
                indexes=self.reflected_data.indexes.get(table, []),
                primary_key=self.reflected_data.pk_constraint.get(table, {}),
                unique_constraints=self.reflected_data.unique_constraints.get(
                    table, []
                ),
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
        **kwargs,
    ):
        super().__init__(
            reflected_data,
            sorted_tables_and_fks,
            schema,
            add_comments,
            create_table_args,
            use_camel_case,
            **kwargs,
        )
        self.relationships = defaultdict(list)
        self.relation_names_map = defaultdict(list)
        self.table_column_map = defaultdict(set)
        self.m2m_associated_tables = []

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
                self.import_path_resolver.insert(make_in_file_obj(column_name))

                if column.get("nullable"):
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

    def collect_imports(self):
        self.resolve_relationships()
        super().collect_imports()

    def _create_relationship_join(
        self, secondary_table: Tuple[Optional[str], str], foreign_key: Dict[str, Any]
    ):
        constrained_columns = foreign_key["constrained_columns"]
        referred_columns = foreign_key["referred_columns"]
        secondary_table_class_name = self.table_class_name_map[secondary_table]
        if len(constrained_columns) == 1:
            constrained_column = constrained_columns[0]
            return StringReprWrapper(
                f"{referred_columns[0]} "
                f"== {secondary_table_class_name}.c.{constrained_column}"
            )

    def handle_m2m_relations(
        self,
        secondary_table: Tuple[Optional[str], str],
        foreign_keys: List[Dict[str, Any]],
        self_referencing: bool = False,
    ):
        secondary_table_class_name = self.table_class_name_map[secondary_table]

        for index, main_foreign_key in enumerate(foreign_keys, start=1):
            main_table = (
                main_foreign_key["referred_schema"],
                main_foreign_key["referred_table"],
            )

            if not self.reflected_data.pk_constraint.get(main_table):
                continue

            main_table_class = self.table_class_name_map[main_table]
            for target_fk in foreign_keys[index:]:
                target_table = target_fk["referred_schema"], target_fk["referred_table"]

                if not self.reflected_data.pk_constraint.get(target_table):
                    continue

                target_table_class = self.table_class_name_map[target_table]

                relationship_name = self.create_to_relation_attribute_name(
                    main_table,
                    target_table,
                    SQLRelationshipType.m2m,
                    target_fk["constrained_columns"],
                )

                back_populate_name = self.create_to_relation_attribute_name(
                    target_table,
                    main_table,
                    SQLRelationshipType.m2m,
                    main_foreign_key["constrained_columns"],
                )

                main_table_relationship_data = {
                    "attribute_name": relationship_name,
                    "target_class": target_table_class,
                    "back_populates": back_populate_name,
                    "relation_type": SQLRelationshipType.m2m,
                    "nullable": False,
                    "secondary_table": secondary_table_class_name,
                }

                reverse_relationship_data = {
                    "attribute_name": back_populate_name,
                    "target_class": main_table_class,
                    "back_populates": relationship_name,
                    "relation_type": SQLRelationshipType.m2m,
                    "nullable": False,
                    "secondary_table": secondary_table_class_name,
                }
                if self_referencing:
                    primary_join = self._create_relationship_join(
                        secondary_table, main_foreign_key
                    )
                    secondary_join = self._create_relationship_join(
                        secondary_table, target_fk
                    )
                    main_table_relationship_data["primaryjoin"] = primary_join
                    main_table_relationship_data["secondaryjoin"] = secondary_join

                    reverse_relationship_data["primaryjoin"] = secondary_join
                    reverse_relationship_data["secondaryjoin"] = primary_join

                if main_table_relationship_data not in self.relationships[main_table]:
                    self.relationships[main_table].append(main_table_relationship_data)

                if reverse_relationship_data not in self.relationships[target_table]:
                    self.relationships[target_table].append(reverse_relationship_data)

    def resolve_m2m_relationship(self, table) -> Tuple[bool, bool]:
        try:
            fks = self.reflected_data.foreign_keys[table]
        except KeyError:
            return False, False

        column_names = self.table_column_map[table]
        fk_columns = set()
        target_tables = set()
        for fk in fks:
            constrained_columns = fk["constrained_columns"]
            fk_columns.update(set(constrained_columns))
            target_tables.add((fk["referred_schema"], fk["referred_table"]))

        # pk_columns = set(self.table_pk_map.get(table, []))
        # non_pk_columns = column_names - pk_columns
        # if non_pk_columns == fk_columns or fk_columns == column_names:
        if fk_columns == column_names:
            return bool(target_tables), len(target_tables) == 1

        return False, False

    def resolve_relationship_type_of_fk(self, table, foreign_key):
        fk_columns = foreign_key["constrained_columns"]

        if (
            fk_columns in self.table_unique_cols_map[table]
            or fk_columns == self.table_pk_map[table]
        ):
            return SQLRelationshipType.o2o

        return SQLRelationshipType.o2m

    def table_has_attribute(self, attribute, table):
        columns = self.table_column_map[table]
        relationships = self.relation_names_map[table]
        return attribute in columns or attribute in relationships

    def find_unique_key_for_relation_attribute(
        self,
        attribute_name,
        main_tabel,
        target_table,
        use_singular_suffixes=True,
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

    def _convert_column_name_to_attr_name(self, name):
        if self.use_camel_case:
            return to_camel_case(name).rstrip("Id")

        return to_snake_case(name).rstrip("_id")

    def create_to_relation_attribute_name(
        self, main_table, target_table, relation_type, constrained_columns: List[str]
    ):
        attribute_name = main_table[1]

        # TODO: handle composite primary key
        if len(constrained_columns) == 1:
            attribute_name = self._convert_column_name_to_attr_name(
                constrained_columns[0]
            )

        attribute_name = inflect_engine.to_singular(attribute_name)
        use_singular_suffixes = True

        if relation_type in (SQLRelationshipType.m2o, SQLRelationshipType.m2m):
            use_singular_suffixes = False
            self.import_path_resolver.insert(List)
            attribute_name = inflect_engine.to_plural(attribute_name)

        return self.find_unique_key_for_relation_attribute(
            attribute_name,
            main_table,
            target_table,
            use_singular_suffixes,
        )

    def find_back_population_name_for_non_m2m(
        self,
        attribute_name,
        main_table,
        relation_type,
        target_table,
        self_referencing: bool = False,
    ):
        back_populates = main_table[1]

        if relation_type == SQLRelationshipType.o2o:
            back_populates = inflect_engine.to_singular(back_populates)
            return self.find_unique_key_for_relation_attribute(
                back_populates,
                target_table,
                main_table,
            )

        else:
            parent = "parent"

            if attribute_name.lower().startswith(parent):
                length = len(parent)
                back_populates = attribute_name[length:] or back_populates
                back_populates = "sub_" + back_populates

            elif self_referencing:
                back_populates = "sub_" + attribute_name

            back_populates = inflect_engine.to_plural(back_populates)
        return self.find_unique_key_for_relation_attribute(
            back_populates, target_table, main_table, False
        )

    @staticmethod
    def get_table_name_as_str(table):
        if table[0]:
            return f"{table[0]}{table[1]}"
        else:
            return table[1]

    def resolve_relationships(self):
        for main_table, fks in self.reflected_data.foreign_keys.items():
            m2m, self_referencing = self.resolve_m2m_relationship(main_table)

            if main_table in self.excluded_relationship_tables:
                continue

            if m2m:
                self.m2m_associated_tables.append(main_table)
                self.handle_m2m_relations(main_table, fks, self_referencing)
                continue

            if not self.reflected_data.pk_constraint.get(main_table):
                continue

            main_table_class = self.table_class_name_map[main_table]

            for fk in fks:

                target_table = (fk["referred_schema"], fk["referred_table"])

                if (
                    not self.reflected_data.pk_constraint.get(target_table)
                    or target_table in self.excluded_relationship_tables
                ):
                    continue

                try:
                    target_table_class = self.table_class_name_map[target_table]
                except KeyError:
                    target_table_str = self.get_table_name_as_str(target_table)
                    main_table_str = self.get_table_name_as_str(main_table)
                    logger.warning(
                        "Cannot create relation from %s to %s. Because table %s is not reflected. "
                        % (main_table_str, target_table_str, target_table_str)
                    )
                    continue
                relation_type = self.resolve_relationship_type_of_fk(main_table, fk)
                constrained_columns = fk["constrained_columns"]

                self_referencing = target_table == main_table

                relationship_name = self.create_to_relation_attribute_name(
                    main_table,
                    target_table,
                    relation_type,
                    constrained_columns,
                )

                if (
                    not len(constrained_columns) == 1
                    or relation_type == SQLRelationshipType.o2o
                ):
                    attr_name = main_table[1]

                else:
                    attr_name = constrained_columns[0]

                attr_name = self._convert_column_name_to_attr_name(attr_name)

                back_populate_name = self.find_back_population_name_for_non_m2m(
                    attr_name, main_table, relation_type, target_table, self_referencing
                )

                main_table_relationship_data = {
                    "attribute_name": relationship_name,
                    "target_class": target_table_class,
                    "back_populates": back_populate_name,
                    "relation_type": relation_type,
                    "nullable": False,
                    "secondary_table": None,
                }

                reverse_relationship_data = {
                    "attribute_name": back_populate_name,
                    "target_class": main_table_class,
                    "back_populates": relationship_name,
                    "relation_type": relation_type.reversed_relationship,
                    "nullable": False,
                    "secondary_table": None,
                }

                if self_referencing:
                    referred_columns = fk["referred_columns"][0]
                    remote_side = f"{main_table_class}.{referred_columns}"
                    main_table_relationship_data["remote_side"] = remote_side

                sa_foreign_keys = "["
                for cc in constrained_columns:
                    sa_foreign_keys += f"{main_table_class}.{cc},"
                sa_foreign_keys += "]"
                main_table_relationship_data["foreign_keys"] = sa_foreign_keys
                reverse_relationship_data["foreign_keys"] = sa_foreign_keys

                if main_table_relationship_data not in self.relationships[main_table]:
                    self.relationships[main_table].append(main_table_relationship_data)

                if reverse_relationship_data not in self.relationships[target_table]:
                    self.relationships[target_table].append(reverse_relationship_data)

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

        enums = self.generate_enums()

        tables_generators = []
        for table in reversed(self.sorted_tables):
            if table in self.m2m_associated_tables or not self.table_pk_map.get(table):
                tables_generators.append(
                    TableGenerator(
                        name=table[1],
                        import_path_resolver=self.import_path_resolver,
                        schema=self.schema,
                        metadata_name=self.metadata_name,
                        columns=columns[table],
                        comment=table_comment.get(table, {}),
                        check_constraints=check_constraints.get(table, []),
                        foreign_keys=foreign_keys.get(table, []),
                        indexes=indexes.get(table, []),
                        primary_key=pk_constraint.get(table, {}),
                        unique_constraints=unique_constraints.get(table, []),
                    )
                )

            else:
                generator = DeclarativeTableGenerator(
                    name=table[1],
                    import_path_resolver=self.import_path_resolver,
                    schema=self.schema,
                    metadata_name=self.metadata_name,
                    columns=columns[table],
                    comment=table_comment.get(table, {}),
                    check_constraints=check_constraints.get(table, []),
                    foreign_keys=foreign_keys.get(table, []),
                    indexes=indexes.get(table, []),
                    primary_key=pk_constraint.get(table, {}),
                    unique_constraints=unique_constraints.get(table, []),
                    relationships=self.relationships.get(table, []),
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
        return SQLModel, Field, Relationship, Column, Table, List, registry

    def generate_base_definition(self) -> str:
        class_usage = self.import_path_resolver.get_usage_name(SQLModel)
        registry_usage = self.import_path_resolver.get_usage_name(registry)
        return (
            f"class {self.metadata_name}({class_usage}, registry={registry_usage}()):"
            f"\n    pass"
        )

    def generate(self) -> str:
        self.collect_imports()
        enums = self.generate_enums()

        tables_generators = []
        columns = self.reflected_data.columns
        table_comment = self.reflected_data.table_comment
        check_constraints = self.reflected_data.check_constraints
        foreign_keys = self.reflected_data.foreign_keys
        indexes = self.reflected_data.indexes
        pk_constraint = self.reflected_data.pk_constraint
        unique_constraints = self.reflected_data.unique_constraints

        base_definition = self.generate_base_definition()

        for table in reversed(self.sorted_tables):
            if table in self.m2m_associated_tables or not self.table_pk_map.get(table):
                tables_generators.append(
                    TableGenerator(
                        name=table[1],
                        import_path_resolver=self.import_path_resolver,
                        schema=self.schema,
                        metadata_name=f"{self.metadata_name}.metadata",
                        columns=columns[table],
                        comment=table_comment.get(table, []),
                        check_constraints=check_constraints.get(table, []),
                        foreign_keys=foreign_keys.get(table, []),
                        indexes=indexes.get(table, []),
                        primary_key=pk_constraint.get(table, []),
                        unique_constraints=unique_constraints.get(table, []),
                    )
                )

            else:
                generator = SQLModelTableGenerator(
                    name=table[1],
                    import_path_resolver=self.import_path_resolver,
                    schema=self.schema,
                    metadata_name=self.metadata_name,
                    columns=columns[table],
                    comment=table_comment.get(table, {}),
                    check_constraints=check_constraints.get(table, []),
                    foreign_keys=foreign_keys.get(table, []),
                    indexes=indexes.get(table, []),
                    primary_key=pk_constraint.get(table, {}),
                    unique_constraints=unique_constraints.get(table, []),
                    relationships=self.relationships.get(table, []),
                )
                tables_generators.append(generator)

        import_statements = self.generate_imports()
        tables = [tg.generate() for tg in tables_generators]
        return "\n\n\n".join([import_statements, *enums, base_definition, *tables])


def generate_schema(
    generator_class: Type[CoreSchemaGenerator],
    reflected_data: _ReflectionInfo,
    sorted_tables_and_fks: List[Tuple[Optional[str], List[Tuple[str, Optional[str]]]]],
    schema: str,
    excluded_relationship_tables: Optional[List[Tuple[Optional[str], str]]] = None,
    add_comments: bool = False,
    create_table_args: bool = True,
    use_camel_case: bool = False,
) -> str:
    generator = generator_class(
        reflected_data=reflected_data,
        sorted_tables_and_fks=sorted_tables_and_fks,
        schema=schema,
        add_comments=add_comments,
        create_table_args=create_table_args,
        use_camel_case=use_camel_case,
        excluded_relationship_tables=excluded_relationship_tables,
    )
    return generator.generate()
