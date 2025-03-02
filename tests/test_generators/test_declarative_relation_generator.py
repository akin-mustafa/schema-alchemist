import pytest

from schema_alchemist.constants import SQLRelationshipType
from schema_alchemist.generators import DeclarativeRelationGenerator


@pytest.mark.parametrize(
    "data, expected",
    (
        (
            {
                "attribute_name": "user",
                "target_class": "User",
                "back_populates": "profile",
                "nullable": False,
                "secondary": None,
                "relation_type": SQLRelationshipType.o2o,
            },
            "    user: Mapped['User'] = relationship(back_populates='profile')",
        ),
        (
            {
                "attribute_name": "parent",
                "target_class": "Parent",
                "back_populates": "children",
                "nullable": False,
                "secondary": None,
                "relation_type": SQLRelationshipType.o2m,
            },
            "    parent: Mapped['Parent'] = relationship(" "back_populates='children')",
        ),
        (
            {
                "attribute_name": "children",
                "target_class": "Child",
                "back_populates": "parent",
                "nullable": False,
                "secondary": None,
                "relation_type": SQLRelationshipType.m2o,
                "remote_side": ["id"],
            },
            "    children: Mapped[List['Child']] = relationship("
            "back_populates='parent', remote_side=['id'])",
        ),
        (
            {
                "attribute_name": "attributes",
                "target_class": "Attribute",
                "back_populates": "categories",
                "nullable": False,
                "secondary": None,
                "secondary_table": "CategoryAttribute",
                "relation_type": SQLRelationshipType.m2m,
            },
            "    attributes: Mapped[List['Attribute']] = relationship("
            "secondary=CategoryAttribute, back_populates='categories')",
        ),
    ),
)
def test_declarative_relation_generator(data, expected, pre_configured_ipr):
    generator = DeclarativeRelationGenerator(
        import_path_resolver=pre_configured_ipr, **data
    )

    assert expected == generator.generate()
