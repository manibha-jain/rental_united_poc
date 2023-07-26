from graphql import graphql_mutation
from queries import get_item_query, parse_item_data, items_pagination, paginated_query
from push_avb_units.avb_rentals_united import push_to_ru
import os
from dotenv import load_dotenv

load_dotenv()


def get_available_units_monday():
    responses_data = []
    property_items = parse_item_data(paginated_query(
        get_item_query(os.getenv('AVB_UNITS_BOARD_ID')), items_pagination))

    all_data = []
    for item in property_items:
        try:
            column_values = {x['title']: x['text']
                             for x in item['column_values']}

            date_from = column_values.get('Date From', '')
            date_to = column_values.get('Date To', '')
            number_of_units = column_values.get('Number of Units', '')
            minimum_stay_length = column_values.get('Minimum stay length', '')
            changeover_type_id = column_values.get('Changeover type ID', '')
            property_id = column_values.get('Property IDs', '')

            property_data = []
            property_data.append({
                'date_from': date_from,
                'date_to': date_to,
                'number_of_units': number_of_units,
                'minimum_stay_length': minimum_stay_length,
                'changeover_type_id': changeover_type_id,
                'property_id': property_id
            })
            all_data.extend(property_data)

        except Exception as e:
            print('exception inside function get_available_units_monday::::::::::',  e)

    unique_property_id_list = []
    formatted_data = {}
    for data in all_data:
        if data['property_id'] not in unique_property_id_list:
            data_list = []
            data_list.append(data)
            formatted_data[data['property_id']] = data_list
            unique_property_id_list.append(data['property_id'])
        else:
            previous_data = formatted_data[data['property_id']]
            previous_data.append(data)
            formatted_data[data['property_id']] = previous_data

    print("---formatted_data-----", formatted_data)
    for key, value in formatted_data.items():
        string_head = f"""<MuCalendar PropertyID="{key}">"""
        string_body = ''
        for single_value in value:

            string_body += f"""<Date From="{single_value['date_from']}" To="{single_value['date_to']}">
                            <U>{single_value['number_of_units']}</U>
                            <MS>{single_value['minimum_stay_length']}</MS>
                            <C>{single_value['changeover_type_id']}</C>
                            </Date>"""

        string_tail = f"""</MuCalendar>"""
        formatted_string = string_head+string_body+string_tail
        update_ru_response = push_to_ru(formatted_string)
        responses_data.append(update_ru_response)

    print("-----responses_data----------", responses_data)
    return responses_data