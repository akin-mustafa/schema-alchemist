from __future__ import annotations

import inspect
import keyword
import os
import random
import re
import string
from collections import defaultdict, deque, OrderedDict as ColOrderedDict, namedtuple
from enum import Enum
from sqlalchemy import Enum as SqlEnum, ARRAY
from typing import (
    Type,
    Any,
    List,
    Tuple,
    Dict,
    Optional,
    DefaultDict,
    Set,
    FrozenSet,
    Deque,
    OrderedDict,
    Union,
)

import inflect

DEFAULT_INDENT_CHAR = os.getenv("DEFAULT_IDENT_CHAR", " ")
DEFAULT_INDENT_MULTIPLIER = int(os.getenv("DEFAULT_IDENT_MULTIPLIER", 4))

DEFAULT_INDENTATION = DEFAULT_INDENT_CHAR * DEFAULT_INDENT_MULTIPLIER


class Empty:
    pass


empty = Empty()


class InflectEngine:
    def __init__(self):
        self.engine = inflect.engine()

    def to_singular(self, word: str) -> str:
        singular = self.engine.singular_noun(word)
        return singular if singular else word

    def to_plural(self, word: str) -> str:
        # HACK! plural_noun doesn't work properly if word is already plural
        plural = self.engine.plural_noun(self.to_singular(word))
        return plural if plural else word


inflect_engine = InflectEngine()


class StringReprWrapper:
    __slots__ = ("wrapped",)

    def __init__(self, wrapped: str):
        self.wrapped = wrapped

    def __repr__(self):
        return self.wrapped

    def __eq__(self, other):
        return self.wrapped == other.wrapped


class ImportParts:
    __slots__ = ("module", "main_class", "inner")

    def __init__(self, obj: Any):
        module, maybe_class = self.get_module_and_class(obj)
        main_class = ""
        inner = ""
        if isinstance(obj, str):
            module = obj

        elif module in ("builtins", "__main__"):
            module = ""
            main_class = maybe_class.__name__

        elif maybe_class is not empty:
            main_class, inner = self.parse_qualified_name(maybe_class)

        self.module = module
        self.main_class = main_class
        self.inner = inner

    def __eq__(self, other):
        return (
            self.module == other.module
            and self.main_class == other.main_class
            and self.inner == other.inner
        )

    @staticmethod
    def parse_qualified_name(obj: Any) -> Tuple[str, str]:
        qualified_name = obj.__qualname__
        top_level_name, *rest = qualified_name.split(".", 1)

        rest = rest[0] if rest else ""

        return top_level_name, rest

    @staticmethod
    def get_module_and_class(obj: Any) -> Tuple[str, Type[Any] | Empty]:
        """
        Returns (module_name, class/function/type) for `obj`.
        If `obj` is a module, the second item is None.
        """
        if inspect.ismodule(obj):
            return obj.__name__, empty

        module_name = getattr(obj, "__module__", None)
        if module_name:
            if not hasattr(obj, "__qualname__"):
                obj = type(obj)
            return module_name, obj

        obj = type(obj)
        return obj.__module__, obj

    @property
    def full_import_path(self) -> str:
        if self.main_class:
            return f"{self.module}.{self.main_class}"
        return f"{self.module}"

    @property
    def import_path_resolver_data(self) -> str:
        if not self.main_class and not self.full_import_path.startswith("__file__"):
            return f"__module__.{self.full_import_path}"

        return self.full_import_path

    @property
    def qualified_name(self):
        if self.has_inner_inner:
            return f"{self.main_class}.{self.inner}"
        return f"{self.main_class}"

    @property
    def has_inner_inner(self) -> bool:
        return bool(self.inner)

    def get_usage(self, alias):
        if not alias or alias == self.main_class:
            return self.qualified_name

        if self.has_inner_inner:
            return f"{alias}.{self.inner}"

        return alias


class TrieNode:
    """
    A node in the trie, storing a dictionary of children keyed by token.
    """

    __slots__ = ("children",)

    def __init__(self) -> None:
        self.children: Dict[str, "TrieNode"] = {}

    def __repr__(self) -> str:
        return f"{self.children}"

    def insert_child(self, name, child: TrieNode) -> TrieNode:
        self.children.setdefault(name, child)
        return self.children[name]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TrieNode) and self.children == other.children


class ImportPathResolver:
    """
    A trie for resolving minimal, uniquely identifying import paths.

    Each inserted object or string is converted to a "reversed token" path
    and stored in the trie, so that we can later determine the shortest
    unique suffix of the original import path.
    """

    def __init__(self, *initial_values: Any) -> None:
        self.root = TrieNode()
        self.insert_many(*initial_values)

    def insert(self, value: Any) -> None:
        """
        Insert a value (class, module, or string) into the trie.
        """
        import_path = self.parts_of_import_path(value).import_path_resolver_data

        tokens_reversed = list(reversed(import_path.split(".")))
        current = self.root
        for token in tokens_reversed:
            current = current.insert_child(token, TrieNode())

    def insert_many(self, *values: Any) -> None:
        """
        Insert multiple values into the trie.
        """
        for val in values:
            self.insert(val)

    def get_usage_name(self, value: Any) -> str:
        """
        Extract a minimal, unique suffix (class or last token) for a given
        import path.
        """
        parts = self.parts_of_import_path(value)
        if not parts.module:
            return parts.main_class

        import_path = parts.import_path_resolver_data
        _, suffix = self.find_lcp_parts_for_import(import_path)

        return self._get_alias(suffix, parts)

    @staticmethod
    def _get_alias(suffix, parts):

        alias = "_".join(suffix).strip()
        return parts.get_usage(alias)

    @staticmethod
    def __build_multi_import_statement(
        module,
        imports: List[Tuple[Optional[str], Optional[str]]],
    ) -> str:
        imports = imports or []
        if not imports:
            raise ValueError("No imports specified")

        d = [
            f"{class_name} as {alias}" if alias else class_name
            for class_name, alias in imports
        ]

        joined = f",\n{DEFAULT_INDENTATION}".join(sorted(d))
        return f"from {module} import (\n{DEFAULT_INDENTATION}{joined}\n)"

    @staticmethod
    def __build_single_import_statement(
        module, class_name: Optional[str] = None, alias: Optional[str] = None
    ) -> str:
        statement = f"import {module}"

        if class_name:
            statement = f"from {module} import {class_name}"

        if alias:
            statement = f"{statement} as {alias}"

        return statement

    def build_all_import_statements(self):
        """
        Build import statements for every path that was inserted into the trie,
        by enumerating all leaf nodes. No separate attribute is needed.
        """
        statements = []
        import_parts = defaultdict(list)
        import_data = defaultdict(list)

        self.gather_leaf_paths(self.root, import_parts, (), ())
        for commons, unique_parts in import_parts.items():
            for uniques in unique_parts:
                if not uniques and not commons:
                    continue
                if not commons:
                    *module, obj = uniques
                    module = tuple(module)
                    alias = ()
                else:
                    *module, obj = commons
                    module = tuple(module)
                    alias = (uniques[-1],) + commons
                    module = uniques + module

                if module[0] == "__module__":
                    module = module[1:]

                alias = "_".join(alias).strip().replace("__", "")
                module = ".".join(module).strip()
                if (
                    self.is_builtin_or_keyword(module)
                    or self.is_builtin_or_keyword(obj)
                    or module.startswith("__file__")
                ):
                    continue
                import_data[module].append((obj, alias))
        for module, data in import_data.items():
            if not module:
                for class_name, alias in data:
                    module = class_name
                    class_name = None
                    statement = self.__build_single_import_statement(
                        module, class_name, alias
                    )
                    statements.append(statement)
            elif len(data) == 1:
                statement = self.__build_single_import_statement(module, *data[0])
                statements.append(statement)
            else:
                statement = self.__build_multi_import_statement(module, data)
                statements.append(statement)
        import_statements = [s for s in statements if s.startswith("import")]
        from_statements = [s for s in statements if s.startswith("from")]

        statements = sorted(import_statements) + sorted(from_statements)
        return statements

    def gather_leaf_paths(
        self,
        node: TrieNode,
        imports: DefaultDict,
        common_parts: Tuple = (),
        unique_parts: Tuple = (),
    ) -> DefaultDict[Tuple[str], List[Tuple[str]]]:
        """
        Recursively gather all reversed token paths that end at leaf nodes.
        Each leaf node represents a complete, inserted path.
        """
        if not node.children:
            return imports[common_parts].append(unique_parts)

        for token, child_node in node.children.items():
            uniques = unique_parts
            commons = common_parts

            if len(child_node.children) < 2:
                uniques = (token,) + uniques
            elif uniques:
                commons = (token,) + uniques + common_parts
                uniques = unique_parts = ()
            else:
                commons = (token,) + commons

            self.gather_leaf_paths(child_node, imports, commons, uniques)
        return imports

    @classmethod
    def parts_of_import_path(cls, obj: Any) -> ImportParts:
        """
        Determine the full import path for `obj`. Returns None if the object
        is from a built-in (__main__ or builtins).
        If `obj` is a string, assume it's already a valid import path.
        """
        return ImportParts(obj)

    @classmethod
    def is_builtin_or_keyword(cls, obj: Any) -> bool:
        """
        Check if the given object/string corresponds to the builtins module.
        """
        if isinstance(obj, str):
            return obj in __builtins__ or keyword.iskeyword(obj)

        module_name, _ = ImportParts.get_module_and_class(obj)
        return module_name == "builtins"

    def find_lcp_parts_for_import(
        self, import_path: str
    ) -> Tuple[List[str], List[str]]:
        """
        Split the import path into (prefix, suffix), where suffix is the
        shortest unique import tail determined by the trie.

        If the path is builtin or empty, return ("", path).

        Examples
        --------
        >>> rt = ImportPathResolver()
        >>> rt.insert_many(["a.b.z", "x.y.z"])
        >>> rt.find_lcp_parts_for_import("a.b.z")
        (('a',), ('b', 'z'))
        """
        tokens = import_path.split(".")
        rev_tokens = list(reversed(tokens))
        k = self._find_unique_suffix_length(rev_tokens)

        prefix_tokens = tokens[:-k]
        suffix_tokens = tokens[-k:]

        return prefix_tokens, suffix_tokens

    def _find_unique_suffix_length(self, reversed_tokens: List[str]) -> int:
        """
        Walk down the trie with these reversed tokens. Return the minimal k
        such that after walking k tokens, the current trie node has exactly
        one child. If we never see a node with exactly one child, return
        len(reversed_tokens).
        """
        current = self.root
        for i, token in enumerate(reversed_tokens, start=1):
            current = current.children[token]
            if len(current.children) == 1:
                return i
        return len(reversed_tokens)


def convert_to_class_name(s: str) -> str:
    """
    Convert an arbitrary string into a valid Python class name
    following CamelCase/CapWords convention from PEP 8.

    Examples:
      - "hello world" -> "HelloWorld"
      - "123 invalid!! class" -> "_123InvalidClass"
      - "__some_mixed__Case__" -> "SomeMixedCase"
    """

    if not isinstance(s, str):
        class_name = getattr(s, "__name__", s.__class__.__name__)
        raise ValueError("Invalid argument type: {}".format(class_name))

    s = re.sub(r"[^0-9a-zA-Z]+", " ", s)

    if not s.strip():
        raise ValueError("Class name cannot be empty.")

    words = s.split()
    words = [w[0].upper() + w[1:] for w in words]
    class_name = "".join(words)

    if class_name[0].isdigit():
        class_name = "_" + class_name

    return class_name


def convert_to_attribute_name(s: str) -> str:
    if not isinstance(s, str):
        class_name = getattr(s, "__name__", s.__class__.__name__)
        raise ValueError("Invalid argument type: {}".format(class_name))

    s = re.sub(r"[^0-9a-zA-Z]+", " ", s)

    if not s.strip():
        raise ValueError("Class name cannot be empty.")

    words = s.split()
    attr_name = "_".join(words)

    if attr_name[0].isdigit():
        attr_name = "_" + attr_name
    if ImportPathResolver.is_builtin_or_keyword(attr_name):
        attr_name += "_"
    return attr_name


def create_table_name(table: str, schema: Optional[str] = None) -> str:
    """
    Constructs a fully qualified table name, optionally including the schema.
    """
    table = table.strip()

    if not table:
        raise ValueError("Table name cannot be empty or whitespace.")

    if schema:
        schema = schema.strip()
        return f"{schema}.{table}"

    return table


def create_enum(name, args):
    data = dict(zip(args, args))
    return Enum(name, data)


def to_snake_case(text: str) -> str:
    """
    Converts a given string to snake_case.
    """
    text = re.sub(r"[\-\s]+", "_", text)
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = re.sub(r"([A-Z]+)([A-Z].?)", r"\1_\2", text)
    text = re.sub(r"_+", "_", text)
    return text.lower()


def to_camel_case(text: str) -> str:
    """
    Converts a given string to camelCase.
    """
    if re.search(r"[\-\s_]", text):
        words = re.split(r"[\-\s_]+", text)
        return words[0].lower() + "".join(word.capitalize() for word in words[1:])
    else:
        return text[0].lower() + text[1:] if text else ""


def get_annotation_of_type(type_: Any) -> Any:
    builtin_to_typing = {
        list: List,
        dict: Dict,
        set: Set,
        tuple: Tuple,
        frozenset: FrozenSet,
        deque: Deque,
        defaultdict: DefaultDict,
        ColOrderedDict: OrderedDict,
    }
    return builtin_to_typing.get(type_, type_)


def make_in_file_obj(name: Union[str, Type]) -> str:
    if inspect.isclass(name):
        name = name.__name__
    return f"__file__.{name}"


def resolve_column_type(column: Dict[str, Any], table_class_name: str) -> Any:
    ColumnTypes = namedtuple(
        "ColumnTypes", ["sql_types", "sql_generic_types", "python_types"]
    )

    column_type = column["type"]
    column_name = column["name"]

    if isinstance(column_type, ARRAY):
        column_types = set()
        sql_generic_types = set()
        python_types = set()
        while True:
            column_types.add(column_type.__class__)
            sql_generic_types.add(column_type.as_generic().__class__)
            annotated_type = get_annotation_of_type(column_type.python_type)
            python_types.add(annotated_type)

            if not isinstance(column_type, ARRAY):
                break

            column_type = column_type.item_type
        return ColumnTypes(
            tuple(column_types), tuple(sql_generic_types), tuple(python_types)
        )

    sql_types = (column_type.__class__,)
    sql_generic_types = (column_type.as_generic().__class__,)
    annotated_type = get_annotation_of_type(column_type.python_type)
    python_types = (annotated_type,)

    if isinstance(column_type, SqlEnum):
        name = column_type.name or f"{table_class_name}{column_name}"
        python_types = (make_in_file_obj(name), Enum)

    return ColumnTypes(sql_types, sql_generic_types, python_types)


def generate_random_string(length=10, chars=string.ascii_letters):
    """
    Generate a random string of a given length.

    Parameters:
        length (int): Length of the generated string. Default is 10.
        chars (str): A string of characters to choose from.
                     Default includes ascii letters and digits.

    Returns:
        str: A random string.
    """
    return "".join(random.choice(chars) for _ in range(length))
