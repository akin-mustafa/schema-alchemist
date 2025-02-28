from typing import Union

from sqlalchemy import Engine, Connection


from schema_alchemist.constants import SchemaTypeEnum
from schema_alchemist.generators import SchemaGeneratorFactory
from schema_alchemist.reflection import reflect, get_inspector


def create_schema(
    engine: Union[Engine, Connection],
    schema_type: SchemaTypeEnum,
    schema_name: str,
    reflect_views: bool = False,
) -> str:
    reflected_data = reflect(engine, schema_name, reflect_views=reflect_views)
    inspector = get_inspector(engine)
    sorted_tables = inspector.get_sorted_table_and_fkc_names(schema_name)
    return SchemaGeneratorFactory(
        reflected_data, sorted_tables, schema_type, schema_name
    ).generate()
