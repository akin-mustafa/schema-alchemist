from typing import Union, Type, List, Optional

from sqlalchemy import Engine, Connection


from schema_alchemist.generators import CoreSchemaGenerator, generate_schema
from schema_alchemist.reflection import reflect, get_inspector


def create_schema(
    engine: Union[Engine, Connection],
    generator_class: Type[CoreSchemaGenerator],
    schema_name: str,
    excluded_relationship_tables: Optional[List[str]] = None,
    reflect_views: bool = False,
    use_camel_case: bool = False,
) -> str:
    reflected_data = reflect(engine, schema_name, reflect_views=reflect_views)
    inspector = get_inspector(engine)
    sorted_tables = inspector.get_sorted_table_and_fkc_names(schema_name)
    return generate_schema(
        generator_class=generator_class,
        reflected_data=reflected_data,
        sorted_tables_and_fks=sorted_tables,
        schema=schema_name,
        excluded_relationship_tables=excluded_relationship_tables,
        use_camel_case=use_camel_case,
    )
