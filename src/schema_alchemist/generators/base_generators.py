import abc
import inspect
from enum import Enum
from inspect import Parameter
from typing import (
    Optional,
    List,
    Any,
    Dict,
    Sequence,
    Type,
)

from schema_alchemist.utils import (
    ImportPathResolver,
    DEFAULT_INDENTATION,
    convert_to_attribute_name,
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
        params = []
        has_var_arg = bool(
            [
                arg
                for arg in func_parameters.values()
                if arg.kind == Parameter.VAR_POSITIONAL
            ]
        )

        for name in override_positional_only:
            parameter = func_parameters.pop(name)
            value = parameters.get(name, parameter.default)
            params.append(value.__repr__())

        for name, parameter in func_parameters.items():
            value = parameters.get(name, parameter.default)
            if (
                parameter.kind == Parameter.POSITIONAL_ONLY
                or name in override_positional_only
            ) or (
                parameter.kind == Parameter.POSITIONAL_OR_KEYWORD
                and has_var_arg
                and not override_positional_only
                and value is not parameter.default
            ):
                params.append(value.__repr__())

            elif (
                parameter.kind == Parameter.VAR_POSITIONAL
                and value is not parameter.default
            ):
                values = value or []
                for val in values:
                    params.append(val.__repr__())

            elif value is not parameter.default:
                params.append(f"{name}={value!r}")

        params = ", ".join(params)
        func_name = self.import_path_resolver.get_usage_name(func)
        return f"{func_name}({params})"


class EnumGenerator:
    def __init__(self, name, items, import_path_resolver, indentation=None):
        default_indent = DEFAULT_INDENTATION
        self.import_path_resolver = import_path_resolver
        self.indentation = default_indent if indentation is None else indentation
        self.name = name
        self.items = items

    def find_attribute_name(self):
        attr_name = generate_random_string()
        while attr_name in self.items:
            attr_name = generate_random_string()
        return convert_to_attribute_name(attr_name)

    def generate(self):
        enum_usage = self.import_path_resolver.get_usage_name(Enum)
        lines = [f"class {self.name}({enum_usage}):"]
        for item in self.items:
            try:
                attr_name = convert_to_attribute_name(item)
            except ValueError:
                attr_name = self.find_attribute_name()
            lines.append(f"{self.indentation}{attr_name} = {item!r}")
        return "\n".join(lines)
