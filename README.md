# Schema Alchemist

Schema Alchemist is a Python library designed to facilitate the generation of SQLAlchemy and SQLModel schemas from existing database schemas. It provides tools to generate table definitions, column definitions, relationships, and more, making it easier to work with complex database schemas in Python.

## Features

- Generate SQLAlchemy and SQLModel table definitions from existing database schemas.
- Support for various SQLAlchemy column types, including computed columns, identity columns, and more.
- Generate relationships between tables, including one-to-many, many-to-one, and many-to-many relationships.
- Support for generating enums and other constraints.
- Customizable options for naming conventions, including camel case and snake case.
- Ability to exclude specific tables from relationship generation.

## Installation

You can install Schema Alchemist using pip:

```bash
pip install schema-alchemist
```

## Usage
### Basic Usage
To generate SQLAlchemy schemas from an existing database schema, you can use the `CoreSchemaGenerator` class:

```python
from schema_alchemist.generators.schema_generators import CoreSchemaGenerator
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector

engine = create_engine('sqlite:///example.db')

inspector = Inspector.from_engine(engine)
reflected_data = inspector.reflect()
sorted_tables_and_fks = inspector.get_sorted_table_and_fkc_names()

generator = CoreSchemaGenerator(reflected_data, sorted_tables_and_fks)
schema = generator.generate()

print(schema)
```

### Generating SQLModel Schemas
To generate SQLModel schemas, you can use the `SQLModelSchemaGenerator` class:

```python
from schema_alchemist.generators.schema_generators import SQLModelSchemaGenerator

generator = SQLModelSchemaGenerator(reflected_data, sorted_tables_and_fks)
schema = generator.generate()
print(schema)
```

## Contributing
Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request on GitHub.

## License
Schema Alchemist is licensed under the MIT License. See the LICENSE file for more information.
