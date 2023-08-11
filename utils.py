
from graphql import graphql_mutation
from queries import get_item_query, parse_item_data, items_pagination, paginated_subitems_query, paginated_query, change_item_value, get_item_subitem_query
from rentals_united import push_to_ru, update_to_ru
import os
from dotenv import load_dotenv
from sync_rental_to_monday.sync_rental_united import pull_list_of_properties_from_ru


load_dotenv()


def get_composition_rooms(property_id):
    filtered_comp_room_id = []

    composition_rooms = parse_item_data(paginated_subitems_query(
        get_item_subitem_query(os.getenv('COMP_ROOMS_BOARD_ID')), items_pagination))

    for comp_room_item in composition_rooms:
        properties_column = comp_room_item['column_values'][2]['text']
        if properties_column is not None and str(property_id) in properties_column and comp_room_item['subitems']:
            comp_room_id = comp_room_item['column_values'][1]['text']
            subitems = []
            for comp_subitem in comp_room_item['subitems']:
                comp_room_property_col = comp_subitem['column_values'][1]['text']
                if comp_room_property_col is not None and str(property_id) in comp_room_property_col:
                    subitem_id = comp_subitem['column_values'][0]['text']
                    subitems.append({'id': subitem_id})
            filtered_comp_room_id.append({
                'comp_room_id': comp_room_id,
                'subitems': subitems
            })

    print(filtered_comp_room_id)
    return filtered_comp_room_id


def get_item_amenities(property_id):
    filtered_amenity_ids = set()

    items_amenities = parse_item_data(paginated_query(
        get_item_query(os.getenv('AMENITIES_BOARD_ID')), items_pagination))

    for amenity_item in items_amenities:
        amenity_item['column_values'][0]['text']

        if str(property_id) in str(amenity_item['column_values'][1]['text']):
            filtered_amenity_ids.add(amenity_item['column_values'][0]['text'])

    print(filtered_amenity_ids)
    return filtered_amenity_ids


def update_column_value(column_id, column_value):
    print(column_id, column_value)
    try:
        update_column_item = graphql_mutation(change_item_value(
            os.getenv('PROPERTIES_BOARD_ID'), 1222467315, str(column_id), str(column_value)))
        # Handle the response and perform necessary actions after successful update
        if 'error_code' in update_column_item:
            error_message = update_column_item.get('error_message')
            error_data = update_column_item.get('error_data', {})
            raise Exception(
                f"Error updating column value: {error_message}. Item ID: {error_data.get('item_id')}")

        if 'data' in update_column_item and 'change_simple_column_value' in update_column_item['data']:
            return "Column value updated successfully."
        else:
            raise Exception("Failed to update column value.")

    except Exception as e:
        # Handle exceptions and error cases
        print("Error updating column value:", str(e))


def get_duplicate_listing(name, duplicate=False):
    try:
        rental_property_id = ''
        rentals_listing_data = pull_list_of_properties_from_ru()
        if rentals_listing_data is None:
            raise Exception("error while fetching rentals united data.")

        for rental_listing_data in rentals_listing_data:
            ru_listing_data = rental_listing_data.get('Pull_ListSpecProp_RS')
            ru_property_data = ru_listing_data.get('Property')
            ru_listing_name = ru_property_data.get('Name')
            if ru_listing_name is not None and ru_listing_name.strip() == name.strip():
                duplicate = True
                rental_property_id = rental_listing_data.get('property_id')
                break

        return duplicate, rental_property_id

    except Exception as e:
        # Handle exceptions and error cases
        raise Exception("error in get_duplicate_listing: " + str(e))


def get_properties_monday():
    responses_data = []
    property_items = parse_item_data(paginated_query(
        get_item_query(os.getenv('PROPERTIES_BOARD_ID')), items_pagination))
    # print('property_items..............', property_items)

    for item in property_items:
        try:
            # Name, ID, Property ID, Property Information etc..

            # Get Columns Values
            column_values = {x['title']: x['text']
                             for x in item['column_values']}

            name = item['name']
            item_id = item['id']
            rentals_united_id_field = [
                x['id'] for x in item['column_values'] if x['title'] == 'Rentals United ID']

            print('column_values.............', column_values)

            property_id = column_values.get('Property ID', '')
            listing_name = column_values.get('Listing Name', '')
            detailed_location = column_values.get('Detailed Location', '')
            detailed_location_id = column_values.get(
                'Detailed Location ID', '')
            cleaning_fee = column_values.get('Cleaning Price', '')
            property_space = column_values.get('Space', '')
            standard_guests = column_values.get('Standard Guests', '')
            can_sleep_max = column_values.get('Can Sleep Max', '')
            property_type_id = column_values.get('Property Type ID', '')
            no_of_units = column_values.get('No Of Units', '')
            property_floor = column_values.get('Floor', '')
            street = column_values.get('Street', '')
            zip_code = column_values.get('Zip Code', '')
            longitude = column_values.get('Longitude', '')
            latitude = column_values.get('Latitude', '')
            landlord_name = column_values.get('Landlord Name', '')
            landlord_email = column_values.get('Landlord Email', '')
            landlord_phone = column_values.get('Landlord Phone', '')
            deposit = column_values.get('Deposit', '')
            deposit_type_id = column_values.get('Deposit Type ID', '')
            security_deposit = column_values.get('Security Deposit', '')
            security_deposit_id = column_values.get(
                'Security Deposit Type ID', '')

            description = column_values.get('Description', '')

            if property_id:
                amenity_ids = get_item_amenities(property_id)

                # Call comp_rooms without any iteration
                comp_rooms = get_composition_rooms(property_id)

                modified_property_id = f"{property_id}-2"
                modified_comp_rooms = get_composition_rooms(
                    modified_property_id)

                comp_rooms.extend(modified_comp_rooms)

            property_data = []
            print(comp_rooms)
            # Append the variables to the property_list
            property_data.append({
                'name': name,
                'item_id': item_id,
                'property_id': property_id,
                'listing_name': listing_name,
                'detailed_location': detailed_location,
                'detailed_location_id': detailed_location_id,
                'cleaning_fee': cleaning_fee,
                'property_space': property_space,
                'standard_guests': standard_guests,
                'can_sleep_max': can_sleep_max,
                'property_type_id': property_type_id,
                'no_of_units': no_of_units,
                'property_floor': property_floor,
                'street': street,
                'zip_code': zip_code,
                'longitude': longitude,
                'latitude': latitude,
                'landlord_name': landlord_name,
                'landlord_email': landlord_email,
                'landlord_phone': landlord_phone,
                'deposit': deposit,
                'deposit_type_id': deposit_type_id,
                'security_deposit': security_deposit,
                'security_deposit_id': security_deposit_id,
                'description': description,
                'amenity_ids': amenity_ids,
                'comp_rooms': comp_rooms
            })

            print(property_data)
            duplicate, rental_property_id = get_duplicate_listing(property_data[0].get('name'))
            if duplicate == False:
                update_ru_response = push_to_ru(property_data)
            else:
                update_ru_response = update_to_ru(property_data, rental_property_id)
                # if update_ru_response[0]['status_id'] == '0':
                #     update_monday_record = update_column_value(
                #         item_id, rentals_united_id_field[0], update_ru_response[0]['preoprty_id'])
                # print(update_monday_record)

            responses_data.append(update_ru_response)
        except Exception as e:
            raise Exception("error in get_properties_monday: " + str(e))

    # Print the list of update_responses
    print(responses_data)
    return responses_data
