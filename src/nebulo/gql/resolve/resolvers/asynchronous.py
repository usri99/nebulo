from __future__ import annotations

import json
import typing

from nebulo.config import Config
from nebulo.gql.alias import (
    CompositeType,
    ConnectionType,
    CreatePayloadType,
    MutationPayloadType,
    ObjectType,
    ResolveInfo,
    ScalarType,
    TableType,
    UpdatePayloadType,
)
from nebulo.gql.parse_info import parse_resolve_info
from nebulo.gql.relay.node_interface import NodeIdStructure
from nebulo.gql.resolve.transpile.mutation_builder import build_insert, build_update
from nebulo.gql.resolve.transpile.query_builder import sql_builder, sql_finalize


async def async_resolver(_, info: ResolveInfo, **kwargs) -> typing.Any:
    """Awaitable GraphQL Entrypoint resolver

    Expects:
        info.context['database'] to contain a databases.Database
    """
    context = info.context
    database = context["database"]
    jwt_claims = context["jwt_claims"]
    tree = parse_resolve_info(info)

    async with database.transaction():
        # GraphQL automatically resolves the top level object name
        # At time of writing, only required for scalar functions
        for claim_key, claim_value in jwt_claims.items():
            await database.execute(f"set local jwt.claims.{claim_key} to {claim_value};")

        if isinstance(tree.return_type, MutationPayloadType):
            stmt = build_insert(tree) if isinstance(tree.return_type, CreatePayloadType) else build_update(tree)

            row = json.loads((await database.fetch_one(query=stmt))["nodeId"])
            node_id = NodeIdStructure.from_dict(row)

            maybe_mutation_id = tree.args["input"].get("clientMutationId")
            mutation_id_alias = next(
                iter([x.alias for x in tree.fields if x.name == "clientMutationId"]), "clientMutationId"
            )
            node_id_alias = next(iter([x.alias for x in tree.fields if x.name == "nodeId"]), "nodeId")
            output_row_name: str = Config.table_name_mapper(tree.return_type.sqla_model)
            result = {tree.alias: {mutation_id_alias: maybe_mutation_id}, node_id_alias: node_id}
            query_tree = next(iter([x for x in tree.fields if x.name == output_row_name]), None)
            if query_tree:
                # Set the nodeid of the newly created record as an arg
                query_tree.args["nodeId"] = node_id
                base_query = sql_builder(query_tree)
                query = sql_finalize(query_tree.name, base_query)
                coro_result: str = (await database.fetch_one(query=query))["json"]
                sql_result = json.loads(coro_result)
                result[tree.alias].update(sql_result)

        elif isinstance(tree.return_type, ObjectType):
            base_query = sql_builder(tree)
            # print(base_query)
            query = sql_finalize(tree.name, base_query)

            # from sqlalchemy import create_engine
            # dial_eng = create_engine("postgresql://")
            # query = str(query.compile(compile_kwargs={"literal_binds": True, "engine": dial_eng}))
            # print(query)
            query_coro = database.fetch_one(query=query)
            coro_result = await query_coro
            str_result: str = coro_result["json"]  # type: ignore
            result = json.loads(str_result)
            # print(result)
        elif isinstance(tree.return_type, ScalarType):
            base_query = sql_builder(tree)
            query_coro = database.fetch_one(query=base_query)
            scalar_result = await query_coro
            result = next(scalar_result._row.values())  # pylint: disable=protected-access

        else:
            raise Exception("sql builder could not handle return type")

    # Stash result on context to enable dumb resolvers to not fail
    # print(json.dumps(result))
    context["result"] = result
    return result
