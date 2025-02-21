from __future__ import annotations

import inspect
from typing import Type, Any, List, Tuple, Dict


class Empty:
    pass


empty = Empty()


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

        if self.qualified_name:
            return f"{alias}.{self.qualified_name}"

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
        import_path = self.parts_of_import_path(value).full_import_path
        import_path = self._append_dot_if_needed(import_path)

        tokens_reversed = list(reversed(import_path.split(".")))
        current = self.root
        for token in tokens_reversed:
            current = current.insert_child(token, TrieNode())

    @staticmethod
    def _append_dot_if_needed(import_path):
        if import_path and "." not in import_path:
            import_path = f".{import_path}"
        return import_path

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

        import_path = parts.full_import_path
        _, suffix = self.find_lcp_parts_for_import(import_path)

        return self._get_alias(suffix, parts)

    def _get_alias(self, suffix, parts):
        if parts.main_class in self.root.children:
            suffix = suffix[:-1]

        alias = "_".join(suffix).strip()
        return parts.get_usage(alias)

    def build_import_statement(self, value: str) -> str:
        """
        Transform a module path into an import statement, using the shortest
        unique suffix for the final part.

        Examples
        --------
        >>> rt = ImportPathResolver()
        >>> rt.insert_many(["a.b.z", "x.y.z"])
        >>> rt.build_import_statement("a.b.z")
        'from a import b.z'
        """
        prefix, suffix = self.find_lcp_parts_for_import(value)
        prefix = ".".join(prefix)
        suffix = ".".join(suffix)
        if prefix:
            return f"from {prefix} import {suffix}"
        return f"import {suffix}"

    def build_all_import_statements(self) -> List[str]:
        """
        Build import statements for every path that was inserted into the trie,
        by enumerating all leaf nodes. No separate attribute is needed.
        """
        all_paths = []
        for reversed_tokens in self._gather_leaf_paths(self.root, []):
            forward_path = ".".join(reversed(reversed_tokens))
            # forward_path = forward_path.lstrip(".")
            all_paths.append(self.build_import_statement(forward_path))

        return sorted(all_paths)

    def _gather_leaf_paths(
        self, node: TrieNode, reversed_tokens_so_far: List[str]
    ) -> List[List[str]]:
        """
        Recursively gather all reversed token paths that end at leaf nodes.
        Each leaf node represents a complete, inserted path.
        """
        if not node.children:
            return [reversed_tokens_so_far]

        all_paths = []
        for token, child_node in node.children.items():
            all_paths.extend(
                self._gather_leaf_paths(child_node, reversed_tokens_so_far + [token])
            )
        return all_paths

    @classmethod
    def parts_of_import_path(cls, obj: Any) -> ImportParts:
        """
        Determine the full import path for `obj`. Returns None if the object
        is from a built-in (__main__ or builtins).
        If `obj` is a string, assume it's already a valid import path.
        """
        return ImportParts(obj)

    @classmethod
    def is_builtin(cls, obj: Any) -> bool:
        """
        Check if the given object/string corresponds to the builtins module.
        """
        if isinstance(obj, str) and obj in dir(__builtins__):
            return True

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
