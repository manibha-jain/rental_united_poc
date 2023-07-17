import requests
import os

def _build_headers():
    """
    Setup headers for API

    Returns:
        dict: required headers for hostaway
    """
    # Construct headers with API key for GraphQL API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': os.getenv('MONDAY_API_KEY')
    }
    return headers

def get_board_columns(board_id):
    '''
    Get all board columns

    Args:
        board_id (string)

    Returns:
        column_dict (dictionary)

    Raises:
        Exception - if unable to get board columns

    '''
    try:
        column_dict = {}
        query = 'query($board_id: Int!) {boards(ids:[$board_id]) {name columns { title id type}}}'

        variables = {
            'board_id': int(board_id),
        }

        response = hit_monday_api(query,variables)
        columns = response['boards'][0]['columns']


        for col in columns:
            column_dict[col['title']] = col['id']

        return column_dict
    except Exception as e:
        print(f"error in get_board_columns")

def  hit_monday_api(query,variables):
    '''
    Hit monday api with payload and headers

    Args:
        query (string)
        variables (dictionary)

    Returns:
        data (dictionary)

    Raises:
        Exception - if unable to hit monday api

    '''
    try:
        # Construct payload for GraphQL API
        payload = {'query': query, 'variables': variables}

        response = requests.post(
            os.getenv('MONDAY_API_ENDPOINT'), json=payload, headers=_build_headers())

        if response.status_code == 200 and 'errors' not in response.json():
            data = response.json()
            if 'error_code' in data:
                print(
                f"unable to hit_monday_api inside {response.json()}")
            else:
                return data['data']
        else:
            print(
                f"unable to hit_monday_api {response.json()}")
    except Exception as e:
        print(f"error in hit_monday_api")

def get_group_id(board_id):
    """
    Get group id whose title is 'New Bookings' from board id

    Returns:
        string: group_id
    """
    try:
        query = 'query($board_id: Int!)  {boards (ids:[$board_id]) {groups { id title } }}'
        variables = {
            'board_id': int(board_id),
        }
        payload = {'query': query, 'variables': variables}

        response = requests.post(
            os.getenv('MONDAY_API_ENDPOINT'), json=payload, headers=_build_headers())

        if response.status_code == 200 and 'errors' not in response.json():
            data = response.json()
            all_groups_data = data['data']['boards'][0]['groups']
            # matching_group = list(filter(lambda group: group['id'] if (group['title'].lower() == 'New Bookings'.lower()) else None, all_groups_data))
        else:
            error_response = response.json()
            print(
                f"unable to fetch groups error: {error_response}")
            return None
        return all_groups_data
    except Exception as e:
        print(f"error in get_group_id")
        return None

def get_all_group_items_of_a_single_board(property_board_id):
    query = "query($board_id: Int!) {boards(ids:[$board_id]){groups(ids:[]){items {id name column_values {title value text}}}}}"
    variables = {
        'board_id': int(property_board_id),
    }
    payload = {'query': query, 'variables': variables}

    response = requests.post(
            os.getenv('MONDAY_API_ENDPOINT'), json=payload, headers=_build_headers())

    if response.status_code == 200 and 'errors' not in response.json():
       data = response.json()
       return data['data']['boards'][0]['groups']
    else:
        print(
            f"unable to get_all_group_items_of_a_single_board {response.json()}")