from graphql import graphql_mutation
from queries import get_item_query, parse_item_data, items_pagination, paginated_subitems_query, paginated_query, change_item_value, get_item_subitem_query
from push_avb_units.avb_rentals_united import push_to_ru
import os
from dotenv import load_dotenv


load_dotenv()


def get_properties_monday():
    responses_data = []
    property_items = parse_item_data(paginated_query(
        get_item_query(os.getenv('AVB_UNITS_BOARD_ID')), items_pagination))

    print('property_items..............', property_items)
    all_data = []
    for item in property_items:
        try:
            column_values = {x['title']: x['text']
                             for x in item['column_values']}

            print('column_values.............', column_values)

            date_from = column_values.get('Date From', '')
            date_to = column_values.get('Date To', '')
            number_of_units = column_values.get('Number of Units', '')
            minimum_stay_length = column_values.get('Minimum stay length', '')
            changeover_type_id = column_values.get('Changeover type ID', '')
            property_ids = column_values.get('Property IDs', '')

            property_data = []
            if property_ids is not None and property_ids != '':
                propery_ids_list = [property_id.strip() for property_id in property_ids.split(',')]
                for property_id in propery_ids_list:
                    property_data.append({
                        'date_from': date_from,
                        'date_to': date_to,
                        'number_of_units': number_of_units,
                        'minimum_stay_length': minimum_stay_length,
                        'changeover_type_id': changeover_type_id,
                        'property_ids': property_id
                    })
                all_data.extend(property_data)

        except Exception as e:
            print(e)

    print("-------all_data---------", all_data)

    id_list = []
    dicct = {}
    for x in all_data:
        if x['property_ids'] not in id_list:
            lisst = []
            lisst.append(x)
            dicct[x['property_ids']] = lisst
            id_list.append(x['property_ids'])
        else:
            previous_data = dicct[x['property_ids']]
            previous_data.append(x)
            dicct[x['property_ids']] = previous_data

    print("---dict-----", dicct)
    for x, y in dicct.items():
        abc = f"""<MuCalendar PropertyID="{str(x)}">"""
        abc2 = ''
        for yy in y:
            abc2 += f"""<Date From="{yy['date_from']}" To="{yy['date_to']}">
                            <U>{yy['number_of_units']}</U>
                            <MS>{yy['minimum_stay_length']}</MS>
                            <C>{yy['changeover_type_id']}</C>
                            </Date>"""
        abc3 = f"""</MuCalendar>"""
        teext = abc+abc2+abc3
        print("----teext-----", teext)
        update_ru_response = push_to_ru(teext)
        responses_data.append(update_ru_response)

    print("-----responses_data----------", responses_data)
    return responses_data