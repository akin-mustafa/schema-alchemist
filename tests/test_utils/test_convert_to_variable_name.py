import pytest

from schema_alchemist.utils import convert_to_variable_name, ImportPathResolver


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("HelloWorld", "HelloWorld"),
        ("First Name", "First_Name"),
        ("Comments_/_Notes", "Comments_Notes"),
        ("a---b__c", "a_b_c"),
        ("a__b____c", "a_b_c"),
        ("_already_ok", "_already_ok"),
        ("valid_name", "valid_name"),
        ("IP-v4-v6", "IP_v4_v6"),
    ],
)
def test_normalization(raw, expected):
    assert convert_to_variable_name(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("123abc", "_123abc"),
        ("123", "_123"),
        ("", "_"),
        ("   ", "_"),
        ("@@@@", "_"),
        ("0", "_0"),
    ],
)
def test_leading_invalid_and_empty_cases(raw, expected):
    assert convert_to_variable_name(raw) == expected


def test_non_string_raises_with_type_name():
    with pytest.raises(ValueError) as ei:
        convert_to_variable_name(123)
    assert "int" in str(ei.value)


def test_non_string_raises_with_class_name():
    class Foo: ...

    with pytest.raises(ValueError) as ei:
        convert_to_variable_name(Foo())
    assert "Foo" in str(ei.value)


def test_keyword_gets_trailing_underscore(monkeypatch):
    def fake_is_builtin_or_keyword(s):  # simulate keyword/builtin detection
        return s in {"class", "list"}

    monkeypatch.setattr(
        ImportPathResolver, "is_builtin_or_keyword", fake_is_builtin_or_keyword
    )
    assert convert_to_variable_name("class", True) == "class_"
    assert convert_to_variable_name("Class", True) == "Class"
    assert convert_to_variable_name("List", True) == "List"
    assert convert_to_variable_name("list", True) == "list_"
    assert convert_to_variable_name("myvar", True) == "myvar"


def test_keyword_gets_trailing_underscore_without_import_check(monkeypatch):
    def fake_is_builtin_or_keyword(s):  # simulate keyword/builtin detection
        return s in {"class", "list"}

    monkeypatch.setattr(
        ImportPathResolver, "is_builtin_or_keyword", fake_is_builtin_or_keyword
    )
    assert convert_to_variable_name("class") == "class_"
    assert convert_to_variable_name("list") == "list"
    assert convert_to_variable_name("List") == "List"
    assert convert_to_variable_name("myvar") == "myvar"


def test_idempotency():
    s = "already_valid"
    assert convert_to_variable_name(s) == s
