# pylint: disable=missing-class-docstring,invalid-name
from graphql.type import (
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLID,
    GraphQLInputObjectType,
    GraphQLInt,
    GraphQLInterfaceType,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLResolveInfo,
    GraphQLScalarType,
    GraphQLSchema,
    GraphQLString,
    GraphQLType,
)

# Handle name changes from graphql-core and graphql-core-next
try:
    from graphql.type import GraphQLInputObjectField as GraphQLInputField
except ImportError:
    from graphql.type import GraphQLInputField

Type = GraphQLType
List = GraphQLList
NonNull = GraphQLNonNull
Argument = GraphQLArgument
Boolean = GraphQLBoolean
String = GraphQLString
ScalarType = GraphQLScalarType


class HasSQLAModel:  # pylint: disable= too-few-public-methods
    sqla_table = None


class ObjectType(GraphQLObjectType, HasSQLAModel):
    pass


class ConnectionType(GraphQLObjectType, HasSQLAModel):
    pass


class EdgeType(ObjectType, HasSQLAModel):
    pass


class CursorType(GraphQLScalarType):
    pass


ID = GraphQLID
InterfaceType = GraphQLInterfaceType
Int = GraphQLInt
InputObjectType = GraphQLInputObjectType
InputField = GraphQLInputField
ResolveInfo = GraphQLResolveInfo
EnumType = GraphQLEnumType
EnumValue = GraphQLEnumValue
Schema = GraphQLSchema


class Field(GraphQLField):
    sqla_model = None


class TableType(ObjectType):
    sqla_model = None
    field_to_column = None

class CompositeType(ObjectType):
    sqla_composite = None
