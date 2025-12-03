"""
ezdsl - Easy Domain Specific Languages

A minimal AST node type system for Python 3.12+
"""

from nanodsl.nodes import (
    # Core types
    Node,
    Ref,
    NodeRef,
    Child,
)

from nanodsl.types import (
    # Type definitions
    TypeDef,
    IntType,
    FloatType,
    StrType,
    BoolType,
    NoneType,
    ListType,
    DictType,
    SetType,
    TupleType,
    LiteralType,
    NodeType,
    RefType,
    UnionType,
    TypeVar,
    TypeVarRef,
    TypeParameter,  # Legacy alias for TypeVar
)

from nanodsl.serialization import (
    # Serialization
    to_dict,
    from_dict,
    to_json,
    from_json,
)

from nanodsl.schema import (
    # Schema extraction
    extract_type,
    node_schema,
    all_schemas,
)

from nanodsl.ast import (
    AST,
)

__all__ = [
    # Core types
    "Node",
    "Ref",
    "NodeRef",
    "Child",
    "AST",
    # Type definitions (TypeDef has classmethod register() and get_registered_type())
    "TypeDef",
    "IntType",
    "FloatType",
    "StrType",
    "BoolType",
    "NoneType",
    "ListType",
    "DictType",
    "SetType",
    "TupleType",
    "LiteralType",
    "NodeType",
    "RefType",
    "UnionType",
    "TypeVar",
    "TypeVarRef",
    "TypeParameter",  # Legacy alias
    # Serialization
    "to_dict",
    "from_dict",
    "to_json",
    "from_json",
    # Schema extraction
    "extract_type",
    "node_schema",
    "all_schemas",
]
