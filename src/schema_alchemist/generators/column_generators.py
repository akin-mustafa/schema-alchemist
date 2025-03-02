from copy import deepcopy
from typing import (
    Optional,
    Any,
    Dict,
    Union,
    Sequence,
    Callable,
    Type,
)

from sqlalchemy import (
    Computed,
    Identity,
    Column,
    ForeignKey,
    Enum as SQLAlchemyEnum,
)
from sqlalchemy.engine.interfaces import (
    ReflectedColumn,
)
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.sql.type_api import TypeEngine
from sqlmodel import Field, SQLModel

from schema_alchemist.generators.base_generators import BaseGenerator
from schema_alchemist.utils import (
    StringReprWrapper,
    ImportPathResolver,
    get_annotation_of_type,
)


class ColumnGenerator(BaseGenerator):
    """
    Generator for producing a SQLAlchemy Column(...) declaration,
    optionally with Identity(...) or Computed(...).
    """

    positional_args: Optional[Sequence[str]] = ("name", "type_")

    def __init__(
        self,
        reflected_column: Union[ReflectedColumn, Dict[str, Any]],
        import_path_resolver: ImportPathResolver,
        table_class_name: str,
        use_generic_types: bool = False,
        *args,
        **kwargs,
    ):
        self.reflected_column = reflected_column
        self.table_class_name = table_class_name
        self.foreign_key = self.reflected_column.pop("foreign_key", None)
        self.parameters = deepcopy(reflected_column)
        self.use_generic_types = use_generic_types
        super().__init__(import_path_resolver, *args, **kwargs)
        if self.indentation is not None:
            self.indentation = self.indentation
        else:
            self.indentation = self.default_indentation

    @property
    def klass(self) -> Callable:
        return Column

    @property
    def column_name(self) -> str:
        return self.reflected_column["name"]

    @property
    def column_type(self) -> TypeEngine:
        return self.reflected_column["type"]

    @property
    def column_type_class(self) -> Type[TypeEngine]:
        if self.use_generic_types:
            return self.column_type_as_generic.__class__
        return self.column_type.__class__

    @property
    def column_type_as_generic(self) -> TypeEngine:
        return self.reflected_column["type"].as_generic()

    @property
    def column_nullable(self) -> bool:
        return self.reflected_column.get("nullable")

    @property
    def column_python_type(self) -> Any:
        if isinstance(self.column_type, SQLAlchemyEnum):
            return self.column_type.name or f"{self.table_class_name}{self.column_name}"
        return self.column_type.python_type

    def create_fk_constraint(self) -> StringReprWrapper:
        target_table = self.foreign_key["referred_table"]
        column = self.foreign_key["referred_columns"][0]
        column = f"{target_table}.{column}"
        options = self.foreign_key.get("options") or {}
        parameters = {
            "column": column,
            "name": self.foreign_key.get("name"),
            "comment": self.foreign_key.get("comment"),
            **options,
        }
        fk = self.generate_function_definition(ForeignKey, parameters)
        return StringReprWrapper(fk)

    def __collect_var_args(self):
        args = []

        if self.reflected_column.get("identity"):
            args.append(self.create_column_identity())

        # if self.foreign_key:
        #     args.append(self.create_fk_constraint())

        if self.reflected_column.get("computed"):
            args.append(self.create_column_computed())

        return args

    def create_column_identity(self) -> Optional[StringReprWrapper]:
        identity_params = self.reflected_column.get("identity")
        identity = self.generate_function_definition(Identity, identity_params)
        return StringReprWrapper(identity)

    def create_column_computed(self) -> Optional[StringReprWrapper]:
        try:
            computed_params = self.reflected_column["computed"]
            computed = self.generate_function_definition(Computed, computed_params)
            return StringReprWrapper(computed)
        except KeyError:
            return None

    def __format_column_type(self) -> StringReprWrapper:
        type_usage = self.import_path_resolver.get_usage_name(
            self.column_type.__class__
        )
        type_str = repr(self.column_type)
        type_str = type_usage + type_str.lstrip(self.column_type.__class__.__name__)
        return StringReprWrapper(type_str)

    def _update_parameters(self) -> Dict[str, Any]:
        """
        Modify the self.parameters dictionary to align with typical Column() kwargs:
          - 'default' → 'server_default'
          - 'identity' → Identity(...) object (if present)
          - 'computed' → Computed(...) object (if present)
        """
        self.parameters.pop("type", None)
        self.parameters["server_default"] = self.parameters.pop("default", None)
        self.parameters["type_"] = self.__format_column_type()

        self.parameters["args"] = self.__collect_var_args()
        return self.parameters

    def format_function_call(self) -> str:
        parameters = self._update_parameters()
        return self.generate_function_definition(
            self.klass, parameters, self.positional_args
        )

    def generate(self) -> str:
        """Produce the final Column(...) string, e.g. '    Column("id", Integer, ...)'."""
        return f"{self.indentation}{self.format_function_call()}"


class DeclarativeColumnGenerator(ColumnGenerator):
    """
    Produces a declarative ORM style mapped_column(...) instead of plain Column(...).
    """

    @property
    def klass(self) -> Callable:
        return mapped_column

    @property
    def column_attr_name(self) -> str:
        return self.column_name.replace(" ", "_")

    @property
    def python_annotation(self) -> str:
        """
        String annotation for a typed column, e.g. 'Optional[int]' if it's nullable,
        otherwise 'int'.
        """

        annotation = self._get_annotation()

        if self.column_nullable:
            optional = self.import_path_resolver.get_usage_name(Optional)
            return f"{optional}[{annotation}]"

        return annotation

    def _get_annotation(self):
        annotation = get_annotation_of_type(self.column_python_type)
        annotation = self.import_path_resolver.get_usage_name(annotation)
        return annotation

    def generate(self):
        """
        Example output:
            id: Mapped[Optional[int]] = mapped_column("id", Integer, ...)
        """
        mapped_import_name = self.import_path_resolver.get_usage_name(Mapped)
        return (
            f"{self.indentation}{self.column_attr_name}: "
            f"{mapped_import_name}[{self.python_annotation}] = "
            f"{self.format_function_call()}"
        )


class SQLModelColumnGenerator(DeclarativeColumnGenerator):
    """
    Produces a sqlmodel.Field(...) that internally wraps a Column(...).
    """

    positional_args = None

    def _update_parameters(self) -> Dict[str, Any]:
        sa_column = ColumnGenerator(
            self.reflected_column,
            self.import_path_resolver,
            self.table_class_name,
            indentation="",
        )
        parameters = {"sa_column": StringReprWrapper(sa_column.generate())}
        if self.column_nullable or self.parameters.get("primary_key"):
            parameters["default"] = None
        return parameters

    @property
    def column_attr_name(self) -> str:
        column_name = self.column_name
        while column_name in dir(SQLModel):
            column_name += "_"
        return column_name.replace(" ", "_")

    @property
    def python_annotation(self) -> str:
        """
        String annotation for a typed column, e.g. 'Optional[int]' if it's nullable,
        otherwise 'int'.
        """

        annotation = self._get_annotation()

        if self.column_nullable or self.parameters.get("primary_key"):
            optional = self.import_path_resolver.get_usage_name(Optional)
            return f"{optional}[{annotation}]"

        return annotation

    @property
    def klass(self) -> Callable:
        return Field

    def generate(self):
        """
        Example output:

            id: Optional[int] = Field(sa_column=Column("id", Integer, ...))
        """
        return (
            f"{self.indentation}{self.column_attr_name}: "
            f"{self.python_annotation} = {self.format_function_call()}"
        )
