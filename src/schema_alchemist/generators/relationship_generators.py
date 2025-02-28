from typing import (
    Optional,
    List,
    Any,
    Dict,
    Callable,
)

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Relationship

from schema_alchemist.constants import SQLRelationshipType
from schema_alchemist.generators.base_generators import BaseGenerator
from schema_alchemist.utils import ImportPathResolver, StringReprWrapper


class DeclarativeRelationGenerator(BaseGenerator):

    def __init__(
        self,
        attribute_name: str,
        target_class: str,
        back_populates: str,
        relation_type: SQLRelationshipType,
        import_path_resolver: ImportPathResolver,
        nullable: bool = False,
        secondary_table: Any = None,
        *args,
        **kwargs,
    ):
        super().__init__(import_path_resolver, *args, **kwargs)
        self.attribute_name = attribute_name
        self.target_class = target_class
        self.back_populates = back_populates
        self.nullable = nullable
        self.secondary = secondary_table
        self.relation_type = relation_type

    @property
    def klass(self) -> Callable:
        return relationship

    @property
    def python_annotation(self) -> str:
        annotation = f"'{self.target_class}'"

        if self.nullable:
            optional = self.import_path_resolver.get_usage_name(Optional)
            annotation = f"{optional}[{annotation}]"

        if self.relation_type in (SQLRelationshipType.m2o, SQLRelationshipType.m2m):
            list_usage = self.import_path_resolver.get_usage_name(List)
            annotation = f"{list_usage}[{annotation}]"

        return annotation

    @property
    def parameters(self) -> Dict[str, Any]:
        secondary = self.secondary
        if secondary:
            secondary = StringReprWrapper(secondary)

        return {
            "secondary": secondary,
            "back_populates": self.back_populates,
        }

    def generate_relation(self):
        return self.generate_function_definition(self.klass, self.parameters)

    def generate(self, *args, **kwargs) -> str:
        mapped_import_name = self.import_path_resolver.get_usage_name(Mapped)
        return (
            f"{self.indent}{self.attribute_name}: "
            f"{mapped_import_name}[{self.python_annotation}] = "
            f"{self.generate_relation()}"
        )


class SQLModelRelationGenerator(DeclarativeRelationGenerator):

    @property
    def parameters(self) -> Dict[str, Any]:
        secondary = self.secondary
        if secondary:
            secondary = StringReprWrapper(secondary)
        return {
            "back_populates": self.back_populates,
            "link_model": secondary,
        }

    @property
    def klass(self) -> Callable:
        return Relationship

    def generate(self, *args, **kwargs) -> str:
        return (
            f"{self.indent}{self.attribute_name}: {self.python_annotation} = "
            f"{self.generate_relation()}"
        )
