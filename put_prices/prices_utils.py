import os
from queries import get_item_query, items_pagination, paginated_query, parse_item_data
from put_prices.price_rental_united import push_to_ru

def upload_prices():
    responses_data = []
    price_items = parse_item_data(paginated_query(
        get_item_query(os.getenv('PRICES_BOARD_ID')), items_pagination))

    for item in price_items:
        try:
            # Get Columns Values
            column_values = {x['title']: x['text']
                            for x in item['column_values']}

            property_id = column_values.get('Property Id', '')
            date_from = column_values.get('Date From', '')
            date_to = column_values.get('Date To', '')
            price = column_values.get('Price', '')
            extra = column_values.get('Extra', '')


            property_data = {
                'property_id': property_id,
                'date_from' : date_from,
                'date_to' : date_to,
                'price': price,
                'extra': extra
            }

            update_ru_response = push_to_ru(property_data)

            responses_data.append(update_ru_response)

        except Exception as e:
            print(e, 'error in funxtion upload_prices.')

    # Print the list of update_responses
    print(responses_data)
    return responses_data