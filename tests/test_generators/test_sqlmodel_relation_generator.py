import pytest

from schema_alchemist.constants import SQLRelationshipType
from schema_alchemist.generators import SQLModelRelationGenerator
from schema_alchemist.utils import StringReprWrapper


@pytest.mark.parametrize(
    "data, expected_parameters, expected_relation",
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
            {
                "back_populates": "profile",
                "link_model": None,
            },
            "    user: 'User' = Relationship(back_populates='profile')",
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
            {
                "back_populates": "children",
                "link_model": None,
            },
            "    parent: 'Parent' = Relationship(back_populates='children')",
        ),
        (
            {
                "attribute_name": "children",
                "target_class": "Child",
                "back_populates": "parent",
                "nullable": False,
                "secondary": None,
                "relation_type": SQLRelationshipType.m2o,
            },
            {
                "back_populates": "parent",
                "link_model": None,
            },
            "    children: List['Child'] = Relationship(back_populates='parent')",
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
            {
                "back_populates": "categories",
                "link_model": StringReprWrapper("CategoryAttribute"),
            },
            "    attributes: List['Attribute'] = Relationship("
            "back_populates='categories', link_model=CategoryAttribute)",
        ),
    ),
)
def test_sqlmodel_relation_generator(
    data, expected_parameters, expected_relation, pre_configured_ipr
):
    generator = SQLModelRelationGenerator(
        import_path_resolver=pre_configured_ipr, **data
    )
    assert generator.parameters == expected_parameters
    assert generator.generate() == expected_relation
