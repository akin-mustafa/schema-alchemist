from typing import Any, Optional, Collection, Set, Tuple, Union

from sqlalchemy import Engine, Connection
from sqlalchemy.engine import ObjectKind, ObjectScope
from sqlalchemy.engine.reflection import _ReflectionInfo, Inspector


def get_table_names_to_be_reflected(
    inspector: Inspector,
    schema: Optional[str] = None,
    only: Optional[Collection[str]] = None,
    exclude: Optional[Collection[str]] = None,
    reflect_views: bool = False,
) -> Tuple[Set[str], Set[str]]:
    all_tables = set(inspector.get_table_names(schema))
    allowed_views = []

    if reflect_views:
        allowed_views = inspector.get_view_names(schema)

    all_tables.update(allowed_views)

    if exclude and only:
        raise ValueError("exclude and only parameters are mutually exclusive.")

    filtered_tables = None
    if only is not None:
        only = set(only)
        missing = only - all_tables
        if missing:
            raise ValueError("Following tables don't exist: {}".format(missing))

        filtered_tables = all_tables.union(only)

    elif exclude is not None:
        exclude = set(exclude)
        missing = exclude - all_tables
        if missing:
            raise ValueError("Following tables don't exist: {}".format(missing))
        filtered_tables = all_tables - exclude

    return all_tables, filtered_tables


def get_inspector(bind: Union[Engine, Connection]) -> Inspector:
    return Inspector(bind)


def reflect(
    engine: Union[Engine, Connection],
    schema: Optional[str] = None,
    only: Optional[Collection[str]] = None,
    exclude: Optional[Collection[str]] = None,
    reflect_views: bool = False,
    **kw: Any,
) -> _ReflectionInfo:
    inspector = get_inspector(bind=engine)
    allowed_tables, only = get_table_names_to_be_reflected(
        inspector,
        schema,
        only,
        exclude,
        reflect_views,
    )

    kind = ObjectKind.ANY if reflect_views else ObjectKind.TABLE

    return inspector._get_reflection_info(
        schema,
        filter_names=only,
        available=allowed_tables,
        kind=kind,
        scope=ObjectScope.ANY,
    )
