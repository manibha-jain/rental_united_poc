from graphql import graphql_query


def items_pagination(data):
    return (
        data["data"]["boards"][0]["items"] is not None
        and len(data["data"]["boards"][0]["items"]) == 0
    )


def paginated_query(query: str, pagination_function: callable):
    limit = 10
    page = 1

    array = []

    while True:
        _query = query.replace("##limit##", str(
            limit)).replace("##page##", str(page))
        data = graphql_query(_query)
        if pagination_function(data):
            break
        array.append(data)
        page += 1

    return array


def paginated_subitems_query(query: str, pagination_function: callable):
    limit = 2
    page = 1

    array = []

    while True:
        _query = query.replace("##limit##", str(
            limit)).replace("##page##", str(page))
        data = graphql_query(_query)
        if pagination_function(data):
            break
        array.append(data)
        page += 1

    return array


def get_item_query(board_id: int):
    query = """
        query {
            boards (ids : [%s]) {
                items (limit: ##limit##, page: ##page##) {
                    id
                    name
                    column_values {
                        id
                        text
                        value
                        title
                        type
                    }
                }
            }
        }
    """ % (
        board_id,
    )
    return query


def get_item_subitem_query(board_id: int):
    query = """
        query {
            boards (ids : [%s]) {
                items (limit: ##limit##, page: ##page##) {
                    id
                    name
                    column_values {
                        id
                        text
                        title
                    }
                    subitems {
                        id
                        column_values {
                            id
                            text
                            title
                        }
                    }
                }
            }
        }
    """ % (
        board_id,
    )
    return query


def parse_item_data(data) -> list:
    items = []
    for x in data:
        items.extend(x["data"]["boards"][0]["items"])
    return items


def change_item_value(board_id: int, item_id: int, column_id: str, value: str):
    mutation = f"""
        mutation {{
            change_simple_column_value (item_id: {item_id}, board_id: {board_id},  column_id: "{column_id}", value: "{value}") {{
                id
            }}
        }}
    """
    return mutation
