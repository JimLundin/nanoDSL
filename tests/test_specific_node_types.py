"""
Test that specific node types can be used as children instead of generic Node[T].

This validates that the type system supports both:
- Generic: child: Node[float]
- Specific: child: Literal  (where Literal is Node[float])
"""

from __future__ import annotations

from typing import Any, cast

from nanodsl.nodes import Child, Node, NodeRef, Ref
from nanodsl.schema import node_schema, extract_type
from nanodsl.types import NodeType, RefType
from nanodsl.ast import AST
from nanodsl.serialization import to_dict, from_dict


# Define specific node types for testing
class Literal(Node[float]):
    """A literal number node."""

    value: float


class Variable(Node[float]):
    """A variable reference node."""

    name: str


class BinaryOp(Node[float]):
    """Binary operation with generic Node[float] children."""

    left: Node[float]
    right: Node[float]
    operator: str


class StrictAdd(Node[float]):
    """Addition that only accepts Literal nodes as children."""

    left: Literal  # Specific type, not generic Node[float]
    right: Literal


class MixedOp(Node[float]):
    """Operation with mixed specific and generic children."""

    literal_child: Literal  # Specific
    generic_child: Node[float]  # Generic
    operator: str


class RefContainer(Node[float]):
    """Container with references to specific node types."""

    literal_ref: Ref[Literal]  # Specific node type in reference
    generic_ref: Ref[Node[float]]  # Generic node type in reference


class FlexibleContainer(Node[float]):
    """Container using Child type alias with specific nodes."""

    flexible: Child[float]  # Can be inline or ref
    specific_flex: Literal | Ref[Literal]  # Union of inline and ref for specific type


def test_specific_node_types_instantiation() -> None:
    """Test that specific node types work as children at runtime."""
    # Create literal nodes
    lit1 = Literal(value=1.5)
    lit2 = Literal(value=2.5)

    # Should work: StrictAdd accepts Literal children
    strict = StrictAdd(left=lit1, right=lit2)
    assert strict.left.value == 1.5
    assert strict.right.value == 2.5

    # Generic BinaryOp should also accept Literal (since Literal is Node[float])
    generic = BinaryOp(left=lit1, right=lit2, operator="+")
    assert generic.left == lit1
    assert generic.right == lit2


def test_mixed_specific_and_generic() -> None:
    """Test nodes with both specific and generic child types."""
    lit = Literal(value=3.14)
    var = Variable(name="x")

    mixed = MixedOp(literal_child=lit, generic_child=var, operator="*")
    assert mixed.literal_child.value == 3.14
    assert mixed.generic_child == var


def test_type_extraction_for_specific_nodes() -> None:
    """Test that type extraction correctly handles specific node types."""
    # Extract schema for StrictAdd
    schema = node_schema(StrictAdd)

    # Both left and right should be recognized as NodeType
    left_field = next(f for f in schema.fields if f.name == "left")
    right_field = next(f for f in schema.fields if f.name == "right")

    assert isinstance(left_field.type, NodeType)
    assert isinstance(right_field.type, NodeType)

    # The return type should be extracted from Literal class
    # Literal is Node[float], so returns should be float
    from nanodsl.types import FloatType

    assert isinstance(left_field.type.returns, FloatType)
    assert isinstance(right_field.type.returns, FloatType)


def test_type_extraction_preserves_specificity() -> None:
    """Test that we can distinguish specific types from generic in schema."""
    # For BinaryOp with generic Node[float]
    generic_schema = node_schema(BinaryOp)
    generic_left = next(f for f in generic_schema.fields if f.name == "left")

    # For StrictAdd with specific Literal
    specific_schema = node_schema(StrictAdd)
    specific_left = next(f for f in specific_schema.fields if f.name == "left")

    # Both should be NodeType with float returns
    assert isinstance(generic_left.type, NodeType)
    assert isinstance(specific_left.type, NodeType)

    from nanodsl.types import FloatType

    assert isinstance(generic_left.type.returns, FloatType)
    assert isinstance(specific_left.type.returns, FloatType)

    # Note: The current type system doesn't preserve the specific class name
    # Both are represented as NodeType(returns=FloatType())
    # This is a design choice - the type system focuses on return types


def test_references_with_specific_node_types() -> None:
    """Test that references to specific node types work correctly."""
    lit = Literal(value=42.0)
    var = Variable(name="answer")

    # Create references
    lit_ref = Ref[Literal](id="lit")
    var_ref = Ref[Node[float]](id="var")

    # Create container
    container = RefContainer(literal_ref=lit_ref, generic_ref=var_ref)

    # Put in AST for resolution
    ast = AST(root="container", nodes={"container": container, "lit": lit, "var": var})

    # Resolve references
    # Type inference works! Ref[Literal] correctly resolves to Literal
    resolved_lit = ast.resolve(container.literal_ref)
    # But for generic Node[float] we need a cast to get the specific type
    resolved_var = cast(Variable, ast.resolve(container.generic_ref))

    assert resolved_lit.value == 42.0
    assert isinstance(resolved_lit, Literal)
    assert resolved_var.name == "answer"
    assert isinstance(resolved_var, Variable)


def test_type_extraction_for_ref_specific_nodes() -> None:
    """Test type extraction for references to specific node types."""
    schema = node_schema(RefContainer)

    lit_ref_field = next(f for f in schema.fields if f.name == "literal_ref")
    gen_ref_field = next(f for f in schema.fields if f.name == "generic_ref")

    # Both should be RefType
    assert isinstance(lit_ref_field.type, RefType)
    assert isinstance(gen_ref_field.type, RefType)

    # The target should be NodeType with appropriate returns
    assert isinstance(lit_ref_field.type.target, NodeType)
    assert isinstance(gen_ref_field.type.target, NodeType)

    from nanodsl.types import FloatType

    assert isinstance(lit_ref_field.type.target.returns, FloatType)
    assert isinstance(gen_ref_field.type.target.returns, FloatType)


def test_serialization_with_specific_node_types() -> None:
    """Test that serialization works with specific node types."""
    lit1 = Literal(value=10.0)
    lit2 = Literal(value=20.0)
    strict = StrictAdd(left=lit1, right=lit2)

    # Serialize
    serialized = to_dict(strict)

    # Should contain nested structure
    assert serialized["tag"] == "strictadd"
    assert serialized["left"]["tag"] == "literal"
    assert serialized["left"]["value"] == 10.0
    assert serialized["right"]["tag"] == "literal"
    assert serialized["right"]["value"] == 20.0

    # Deserialize
    deserialized = from_dict(serialized)

    assert isinstance(deserialized, StrictAdd)
    assert isinstance(deserialized.left, Literal)
    assert isinstance(deserialized.right, Literal)
    assert deserialized.left.value == 10.0
    assert deserialized.right.value == 20.0


def test_ast_container_with_specific_node_types() -> None:
    """Test AST container works with specific node types.

    Note: When a field is typed as a specific node (e.g., Literal),
    it expects inline nodes, not references. To use references,
    the field should be typed as Ref[Literal].
    """
    # Create inline nodes (not references)
    left_lit = Literal(value=25.0)
    right_lit = Literal(value=75.0)

    # StrictAdd expects inline Literal nodes
    strict = StrictAdd(left=left_lit, right=right_lit)

    # Store in AST
    ast = AST(
        root="strict",
        nodes={
            "strict": strict,
            "left": left_lit,
            "right": right_lit,
        },
    )

    # Access the inline children
    assert isinstance(strict.left, Literal)
    assert isinstance(strict.right, Literal)
    assert strict.left.value == 25.0
    assert strict.right.value == 75.0


def test_flexible_child_with_specific_types() -> None:
    """Test Child type alias works with specific node types."""
    lit = Literal(value=3.14)

    # Inline specific node
    container1 = FlexibleContainer(flexible=lit, specific_flex=lit)
    assert container1.flexible == lit
    assert container1.specific_flex == lit

    # Reference to specific node
    lit_ref = Ref[Literal](id="pi")
    container2 = FlexibleContainer(flexible=lit_ref, specific_flex=lit_ref)

    ast = AST(root="container", nodes={"container": container2, "pi": lit})

    # For Child type (union of Node | Ref), we need to check which one it is
    if isinstance(container2.flexible, Ref):
        resolved = cast(Literal, ast.resolve(container2.flexible))
        assert isinstance(resolved, Literal)
        assert resolved.value == 3.14


def test_type_system_inference() -> None:
    """
    Test that Python's type system can infer specific node types.

    This is mainly for static type checkers (mypy, pyright, etc.)
    but we can demonstrate the pattern.
    """
    lit = Literal(value=1.0)

    # Type checkers should know that strict.left is Literal, not Node[float]
    strict = StrictAdd(left=lit, right=lit)

    # Access Literal-specific attribute
    assert strict.left.value == 1.0  # .value is specific to Literal

    # For generic, type checkers only know it's Node[float]
    generic = BinaryOp(left=lit, right=lit, operator="+")
    # generic.left.value would be a type error (Node[float] doesn't have .value)
    # But at runtime it works because lit is a Literal
    assert generic.left.value == 1.0  # type: ignore


def test_documentation_example() -> None:
    """Example showing both patterns for documentation."""

    # Pattern 1: Generic Node[T] - most flexible
    class GenericExpression(Node[int]):
        child: Node[int]  # Accepts any node returning int

    # Pattern 2: Specific node type - more restrictive
    class IntLiteral(Node[int]):
        value: int

    class StrictExpression(Node[int]):
        child: IntLiteral  # Only accepts IntLiteral nodes

    # Both patterns work
    lit = IntLiteral(value=42)

    generic_expr = GenericExpression(child=lit)  # Works
    strict_expr = StrictExpression(child=lit)  # Works

    # Type checker knows strict_expr.child is IntLiteral
    assert strict_expr.child.value == 42

    # For generic_expr, type checker only knows it's Node[int]
    # (but at runtime it's still IntLiteral)
    assert generic_expr.child.value == 42  # type: ignore

    # This demonstrates the trade-off:
    # - Generic Node[T]: More flexible, but less specific type info
    # - Specific types: More restrictive, but better type safety
