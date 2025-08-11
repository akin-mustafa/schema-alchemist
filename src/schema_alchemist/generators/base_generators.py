import abc
import inspect
from enum import Enum
from inspect import Parameter
from typing import Optional, List, Any, Dict, Sequence, Type

from schema_alchemist.utils import (
    ImportPathResolver,
    DEFAULT_INDENTATION,
    convert_to_variable_name,
    generate_random_string,
)


class BaseGenerator(abc.ABC):
    positional_or_args_params: Optional[List[str]] = None

    def __init__(
        self,
        import_path_resolver: ImportPathResolver,
        indentation: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.indentation = indentation
        self.import_path_resolver = import_path_resolver

    @property
    def klass(self) -> Optional[Type]:
        return None

    @abc.abstractmethod
    def generate(self, *args, **kwargs):
        pass

    @property
    def indent(self):
        indent = self.indentation or ""
        return indent + self.default_indentation

    @property
    def default_indentation(self) -> str:
        return DEFAULT_INDENTATION

    def generate_function_definition(
        self,
        func,
        parameters: Dict[str, Any],
        override_positional_only: Optional[Sequence[str]] = None,
    ) -> str:
        """
        Given a function or callable-like object plus a dictionary of named
        parameters, produce something like:  MyFunc(x, y, z=1).

        If positional_parameters are provided, those are extracted from the parameters
        dictionary first.
        """
        func_signature = inspect.signature(func)
        func_parameters = dict(func_signature.parameters)
        override_positional_only = override_positional_only or []

        has_var_arg = any(
            p.kind == Parameter.VAR_POSITIONAL for p in func_parameters.values()
        )
        params = []

        for name in override_positional_only:
            parameter = func_parameters.pop(name)
            value = parameters.get(name, parameter.default)
            params.append(repr(value))

        for name, parameter in func_parameters.items():
            value = parameters.get(name, parameter.default)

            if (
                parameter.kind == Parameter.POSITIONAL_ONLY
                or name in override_positional_only
                or (
                    parameter.kind == Parameter.POSITIONAL_OR_KEYWORD
                    and has_var_arg
                    and not override_positional_only
                    and value is not parameter.default
                )
            ):
                params.append(repr(value))

            elif (
                parameter.kind == Parameter.VAR_POSITIONAL
                and value is not parameter.default
            ):
                params.extend(repr(v) for v in (value or []))

            elif value is not parameter.default:
                params.append(f"{name}={value!r}")

        func_name = self.import_path_resolver.get_usage_name(func)
        return f"{func_name}({', '.join(params)})"


class EnumGenerator:
    def __init__(
        self,
        name: str,
        items: Sequence[Any],
        import_path_resolver: ImportPathResolver,
        indentation: Optional[str] = None,
    ):
        self.name = name
        self.items = items
        self.import_path_resolver = import_path_resolver
        self.indentation = DEFAULT_INDENTATION if indentation is None else indentation

    def find_attribute_name(self) -> str:
        while True:
            candidate = convert_to_variable_name(
                generate_random_string(),
                check_import_conflict=True,
            )
            if candidate not in self.items:
                return candidate

    def generate(self) -> str:
        enum_usage = self.import_path_resolver.get_usage_name(Enum)
        lines = [f"class {self.name}({enum_usage}):"]

        for item in self.items:
            try:
                attr_name = convert_to_variable_name(item, check_import_conflict=True)
            except ValueError:
                attr_name = self.find_attribute_name()
            lines.append(f"{self.indentation}{attr_name} = {item!r}")

        return "\n".join(lines)
