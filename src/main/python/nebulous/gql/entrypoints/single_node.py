import json

from sqlalchemy import func, select
from sqlalchemy.sql.expression import literal

from ..alias import Argument, Field, ResolveInfo
from ..convert2.node_interface import NodeID
from ..convert2.table import table_factory
from ..parse_info import parse_resolve_info


class Encoder(json.JSONEncoder):
    def default(self, o):
        return str(o)


def single_node_factory(sqla_model, registry=None) -> Field:
    name = sqla_model.__table__.name
    node = table_factory(sqla_model)
    return Field(node, args={"NodeID": Argument(NodeID)}, resolver=entry_resolver, description="")


def entry_resolver(obj, info: ResolveInfo, **kwargs):
    context = info.context
    session = context["session"]

    return_type = info.return_type
    sqla_model = return_type.sqla_model
    tree = parse_resolve_info(info)
    print(json.dumps(tree, indent=2, cls=Encoder))

    node_model_name, node_model_id = tree["args"]["NodeID"]
    assert sqla_model.__table__.name == node_model_name

    # Apply node argument
    sqla_table = sqla_model.__table__.alias()

    cte = select([sqla_table]).where(sqla_table.c.id == node_model_id).cte("abc")

    # Apply argument filters
    # Argument is not optional in this case
    node_alias = tree["alias"]
    from nebulous.gql.convert2.table import resolve_one

    query = func.json_build_object(literal(node_alias), resolve_one(tree=tree, parent_query=cte))

    result = session.query(query).first()[0]

    # Stash result on context so enable dumb resolvers to not fail
    context["result"] = result
    print(result)
    return result