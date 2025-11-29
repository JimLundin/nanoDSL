"""Tests for ezdsl.types module."""

import pytest

from ezdsl.types import (
    TypeDef,
    PrimitiveType,
    NodeType,
    RefType,
    UnionType,
    GenericType,
    TypeVarType,
    PRIMITIVES,
)


class TestPrimitives:
    """Test primitive type handling."""

    def test_primitives_frozenset(self):
        """Test that PRIMITIVES contains expected types."""
        assert float in PRIMITIVES
        assert int in PRIMITIVES
        assert str in PRIMITIVES
        assert bool in PRIMITIVES
        assert type(None) in PRIMITIVES

    def test_primitives_immutable(self):
        """Test that PRIMITIVES is immutable."""
        with pytest.raises((TypeError, AttributeError)):
            PRIMITIVES.add(list)


class TestPrimitiveType:
    """Test PrimitiveType."""

    def test_primitive_type_creation(self):
        """Test creating a PrimitiveType."""
        pt = PrimitiveType(int)
        assert pt.primitive == int
        assert pt._tag == "primitive"

    def test_primitive_type_frozen(self):
        """Test that PrimitiveType is immutable."""
        pt = PrimitiveType(int)
        with pytest.raises((AttributeError, TypeError)):
            pt.primitive = float


class TestNodeType:
    """Test NodeType."""

    def test_node_type_creation(self):
        """Test creating a NodeType."""
        returns = PrimitiveType(float)
        nt = NodeType(returns)
        assert nt.returns == returns
        assert nt._tag == "node"

    def test_node_type_frozen(self):
        """Test that NodeType is immutable."""
        nt = NodeType(PrimitiveType(int))
        with pytest.raises((AttributeError, TypeError)):
            nt.returns = PrimitiveType(float)


class TestRefType:
    """Test RefType."""

    def test_ref_type_creation(self):
        """Test creating a RefType."""
        target = PrimitiveType(int)
        rt = RefType(target)
        assert rt.target == target
        assert rt._tag == "ref"

    def test_ref_type_frozen(self):
        """Test that RefType is immutable."""
        rt = RefType(PrimitiveType(int))
        with pytest.raises((AttributeError, TypeError)):
            rt.target = PrimitiveType(float)


class TestUnionType:
    """Test UnionType."""

    def test_union_type_creation(self):
        """Test creating a UnionType."""
        options = (PrimitiveType(int), PrimitiveType(str))
        ut = UnionType(options)
        assert ut.options == options
        assert ut._tag == "union"

    def test_union_type_frozen(self):
        """Test that UnionType is immutable."""
        ut = UnionType((PrimitiveType(int), PrimitiveType(str)))
        with pytest.raises((AttributeError, TypeError)):
            ut.options = (PrimitiveType(float),)


class TestGenericType:
    """Test GenericType."""

    def test_generic_type_creation(self):
        """Test creating a GenericType."""
        origin = PrimitiveType(list)
        args = (PrimitiveType(int),)
        gt = GenericType(name="list[int]", origin=origin, args=args)
        assert gt.name == "list[int]"
        assert gt.origin == origin
        assert gt.args == args
        assert gt._tag == "generic"

    def test_generic_type_frozen(self):
        """Test that GenericType is immutable."""
        gt = GenericType(
            name="list[int]",
            origin=PrimitiveType(list),
            args=(PrimitiveType(int),)
        )
        with pytest.raises((AttributeError, TypeError)):
            gt.name = "list[str]"


class TestTypeVarType:
    """Test TypeVarType."""

    def test_typevar_type_basic(self):
        """Test creating a basic TypeVarType (unbounded)."""
        tvt = TypeVarType(name="T")
        assert tvt.name == "T"
        assert tvt.bound is None
        assert tvt._tag == "typevar"

    def test_typevar_type_with_bound(self):
        """Test TypeVarType with bound (like T: int)."""
        bound = PrimitiveType(int)
        tvt = TypeVarType(name="T", bound=bound)
        assert tvt.name == "T"
        assert tvt.bound == bound

    def test_typevar_type_frozen(self):
        """Test that TypeVarType is immutable."""
        tvt = TypeVarType(name="T")
        with pytest.raises((AttributeError, TypeError)):
            tvt.name = "U"


class TestTypeDefRegistry:
    """Test TypeDef registry functionality."""

    def test_type_registry_contains_types(self):
        """Test that type registry contains all type definitions."""
        assert "primitive" in TypeDef._registry
        assert "node" in TypeDef._registry
        assert "ref" in TypeDef._registry
        assert "union" in TypeDef._registry
        assert "generic" in TypeDef._registry
        assert "typevar" in TypeDef._registry

    def test_type_registry_maps_to_classes(self):
        """Test that registry maps tags to correct classes."""
        assert TypeDef._registry["primitive"] == PrimitiveType
        assert TypeDef._registry["node"] == NodeType
        assert TypeDef._registry["ref"] == RefType
        assert TypeDef._registry["union"] == UnionType
        assert TypeDef._registry["generic"] == GenericType
        assert TypeDef._registry["typevar"] == TypeVarType
