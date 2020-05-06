from nebulo.gql.convert.node_interface import to_global_id

SQL_UP = """
CREATE TYPE full_name AS (
    first_name       text,
    last_name        text
);

create table account (
    id serial primary key,
    name full_name not null
);

insert into account(name) values
(('oliver', 'rice'));
"""


def test_query_multiple_fields(gql_exec_builder):
    executor = gql_exec_builder(SQL_UP)
    account_id = 1
    node_id = to_global_id(table_name="account", values=[account_id])
    gql_query = f"""
    {{
        account(nodeId: "{node_id}") {{
            id
            name {{
                first_name
            }}
        }}
    }}
    """

    result = executor(gql_query)
    assert result.errors is None
    assert result.data["account"]["id"] == account_id
    assert result.data["account"]["name"]["first_name"] == "oliver"