"""Tests for how generic Node definitions serialize their types."""

from typing import TypeVar as TypingTypeVar

from nanodsl.schema import extract_type
from nanodsl.types import (
    ListType,
    DictType,
    IntType,
    StrType,
    FloatType,
    TypeVar,
)


def test_type_parameter_in_annotation():
    """Test extracting a type annotation that uses a type parameter."""
    # Simulate: class MyNode[T]:
    #               args: list[T]
    T = TypingTypeVar("T")

    # What does list[T] extract to?
    result = extract_type(list[T])

    assert isinstance(result, ListType)

    # The element is the TypeVar T, not a concrete type!
    assert isinstance(result.element, TypeVar)
    assert result.element.name == "T"


def test_nested_type_parameters():
    """Test extracting nested parameterized types with type parameters."""
    # Simulate: class MyNode[T]:
    #               args: list[dict[str, T]]
    T = TypingTypeVar("T")

    result = extract_type(list[dict[str, T]])

    # Outer: list
    assert isinstance(result, ListType)

    # Middle: dict[str, T]
    dict_type = result.element
    assert isinstance(dict_type, DictType)

    # First arg of dict is str (concrete)
    assert isinstance(dict_type.key, StrType)

    # Second arg of dict is T (type parameter)
    assert isinstance(dict_type.value, TypeVar)
    assert dict_type.value.name == "T"


def test_bounded_type_parameter_in_annotation():
    """Test extracting type annotations with bounded type parameters."""
    # Simulate: class MyNode[T: int]:
    #               value: T
    T = TypingTypeVar("T", bound=int)

    result = extract_type(T)

    assert isinstance(result, TypeVar)
    assert result.name == "T"
    assert result.bound is not None
    assert isinstance(result.bound, IntType)


def test_multiple_type_parameters():
    """Test multiple type parameters in one annotation."""
    # Simulate: class MyNode[K, V]:
    #               data: dict[K, V]
    K = TypingTypeVar("K")
    V = TypingTypeVar("V")

    result = extract_type(dict[K, V])

    assert isinstance(result, DictType)

    # Both key and value are type parameters
    assert isinstance(result.key, TypeVar)
    assert result.key.name == "K"

    assert isinstance(result.value, TypeVar)
    assert result.value.name == "V"
