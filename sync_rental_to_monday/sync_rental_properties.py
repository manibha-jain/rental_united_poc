from sync_rental_to_monday.monday_service import get_board_columns, get_group_id, hit_monday_api, get_composition_rooms_details,get_all_group_items_of_a_single_board
from sync_rental_to_monday.sync_rental_united import pull_list_of_properties_from_ru, pull_min_stay_details_from_ru,pull_prices_of_property_from_ru
import json
import os
from datetime import date
from dateutil.relativedelta import relativedelta

def sync_rental_to_monday():
    try:
        # get property_details from rental_united
        data_dicts = pull_list_of_properties_from_ru()
        for data_dict in data_dicts:

            # fetch values.
            list_of_details = data_dict.get('Pull_ListSpecProp_RS')
            property = list_of_details.get('Property')
            rental_united_id = property.get('rental_united_id', None)
            d_location = property.get('DetailedLocationID')
            coordinates = property.get('Coordinates')
            arrival_instructions = property.get('ArrivalInstructions')
            checkin_out = property.get('CheckInOut')
            deposit = property.get('Deposit')
            security_deposit = property.get('SecurityDeposit')
            descriptions = property.get('Descriptions')
            if descriptions == None:
                 description =None
            else:
                description = descriptions.get('Description')
            if description == None:
                final_desciption = None
            else:
                final_desciption = description[0].get('Text') if type(description) == list else description.get('Text')

            columns = get_board_columns(int(os.getenv('PROPERTIES_BOARD_ID')))

            query = 'mutation ($myItemName: String!, $columnVals: JSON!,$board_id:Int!,$group_id: String!) { create_item (board_id:$board_id,group_id:$group_id, item_name:$myItemName, column_values:$columnVals,create_labels_if_missing:true) { id } }'
            group = get_group_id(int(os.getenv('PROPERTIES_BOARD_ID')))

            print('name..........', property.get('Name'))

            col_vals = json.dumps({
            # columns['rentals_united_id']: int(rental_united_id,
            columns['Property ID']: data_dict.get('property_id'),
            columns['Listing Name']: property.get('Name'),
            columns['Detailed Location']: d_location.get('#text'),
            columns['Detailed Location ID']: d_location.get('@TypeID'),
            columns['Cleaning Price']: property.get('CleaningPrice'),
            columns['Space']: property.get('Space'),
            columns['Standard Guests']: property.get('StandardGuests'),
            columns['Can Sleep Max']: property.get('CanSleepMax'),
            columns['Property Type ID']: property.get('PropertyTypeID'),
            columns['No Of Units']: property.get('NoOfUnits'),
            columns['Floor']: property.get('Floor'),
            columns['Street']: property.get('Street'),
            columns['Zip Code']: property.get('ZipCode'),
            columns['Longitude']: coordinates.get('Longitude'),
            columns['Latitude']: coordinates.get('Latitude'),
            columns['Landlord Name']: arrival_instructions.get('Landlord'),
            columns['Landlord Email']: {'email': arrival_instructions.get('Email'), 'text': arrival_instructions.get('Email')},
            columns['Landlord Phone']: {"phone" : arrival_instructions.get('Phone').replace(' ', ''), "countryShortName": "US"},
            columns['Check In From']: checkin_out.get('CheckInFrom'),
            columns['Check In To']: checkin_out.get('CheckInTo'),
            columns['Check Out Until']: checkin_out.get('CheckOutUntil'),
            columns['Deposit']: deposit.get('#text'),
            columns['Deposit Type ID']: deposit.get('@DepositTypeID'),
            columns['Security Deposit']: security_deposit.get('#text'),
            columns['Security Deposit Type ID']: security_deposit.get('@DepositTypeID'),
            columns['Description']: final_desciption,
            columns['Base Price']: property.get('BasePrice', 0),
            columns['Account Number']: property.get('AccountNo', 000000000),

        })
            variables = {
            'board_id': int(os.getenv('PROPERTIES_BOARD_ID')),
            'columnVals': col_vals,
            'group_id': group[0].get('id'),
            'myItemName': property.get('Name')
            }

            print('Process of saving values in property board of monday.com started>>>>>>>>>>')
            hit_monday_api(query, variables)
            # update available units.
            update_avb_units(data_dict)
            # update composition rooms.
            update_composition_rooms(data_dict)
            # break
            
            print('Process of saving prices in prices board of monday.com started>>>>>>>>>>')
            update_prices(data_dict.get('property_id'), property.get('Name'))
            print('Process of saving prices in prices board of monday.com ended>>>>>>>>>>')

            print('Process of saving amenities in amenities board of monday.com started>>>>>>>>>>')
            list_of_amenities_of_property = property.get('Amenities')
            update_amenities(data_dict.get('property_id'), list_of_amenities_of_property)
            print('Process of saving amenities in amenities board of monday.com ended>>>>>>>>>>')

        print('Process of saving values in property board of monday.com ended>>>>>>>>>>')
    except Exception as e:
        print(e)


def update_avb_units(data_dict):
    try:
        min_stay_data = pull_min_stay_details_from_ru(data_dict.get('property_id'))
        list_of_property_min_stay = min_stay_data.get('Pull_ListPropertyMinStay_RS')
        property_min_stay = list_of_property_min_stay.get('PropertyMinStay')
        min_stay_detials = property_min_stay.get('MinStay')

        if min_stay_detials is not None:
            date_from = min_stay_detials.get('@DateFrom')
            date_to = min_stay_detials.get('@DateTo')
            min_stay = min_stay_detials.get('#text')
            columns = get_board_columns(int(os.getenv('AVB_UNITS_BOARD_ID')))
            query = 'mutation ($myItemName: String!, $columnVals: JSON!,$board_id:Int!,$group_id: String!) { create_item (board_id:$board_id,group_id:$group_id, item_name:$myItemName, column_values:$columnVals,create_labels_if_missing:true) { id } }'
            group = get_group_id(int(os.getenv('AVB_UNITS_BOARD_ID')))
            list_of_details = data_dict.get('Pull_ListSpecProp_RS')
            property = list_of_details.get('Property')

            col_vals = json.dumps({
                columns['Name']: property.get('Name'),
                columns['Date From']: date_from,
                columns['Date To']: date_to,
                columns['Number of Units']: property.get('NoOfUnits'),
                columns['Minimum stay length']: min_stay,
                columns['Changeover type ID']: 4,
                columns['Property IDs']: {"labels":[data_dict.get('property_id')]}
                })
            variables = {
                'board_id': int(os.getenv('AVB_UNITS_BOARD_ID')),
                'columnVals': col_vals,
                'group_id': group[0].get('id'),
                'myItemName': property.get('Name')
                }
            print('Process of saving avb_units in monday.com started>>>>>>>>>>')
            hit_monday_api(query, variables)
            print('Process of saving avb_units in monday.com ended>>>>>>>>>>')

    except Exception as e:
        print("error in update_avb_units::::", e)

def update_composition_rooms(data_dict):
    try:
        composition_room_ids = []
        list_of_details = data_dict.get('Pull_ListSpecProp_RS')
        property = list_of_details.get('Property')
        composition_rooms_amenties = property.get('CompositionRoomsAmenities')
        if composition_rooms_amenties is not None and composition_rooms_amenties != '':
            composition_room_details = composition_rooms_amenties.get('CompositionRoomAmenities')
            if type(composition_room_details) == dict:
                if composition_room_details.get('@CompositionRoomID') not in composition_room_ids:
                    composition_room_ids.append(composition_room_details.get('@CompositionRoomID'))
            else:
                for single_composition_room in composition_room_details:
                    if single_composition_room.get('@CompositionRoomID') not in composition_room_ids:
                        composition_room_ids.append(single_composition_room.get('@CompositionRoomID'))
        print("-----------composition_room_ids-------", composition_room_ids)
        print("----------property_id----------", data_dict.get('property_id'))
        composition_room_values = get_composition_rooms_details()

        for composition_room_id in composition_room_ids:
            for single_comp_room_value in composition_room_values:
                updated_value = ''
                if int(composition_room_id) == int(single_comp_room_value.get('comp_room_id')):
                    if single_comp_room_value.get('property_id') is None or single_comp_room_value.get('property_id') == '':
                        updated_value = data_dict.get('property_id')
                    else:
                        previous_value = single_comp_room_value.get('property_id')
                        if str(data_dict.get('property_id')) not in str(previous_value):
                            updated_value = str(previous_value) + ', ' +str(data_dict.get('property_id'))
                    if updated_value != '':

                        query = 'mutation ($columnVals: String!,$board_id:Int!,$item_id:Int!) { change_simple_column_value (item_id:$item_id,board_id:$board_id,column_id:"text",value:$columnVals) { id } }'
                        variables = {
                            'board_id': int(os.getenv('COMP_ROOMS_BOARD_ID')),
                            'columnVals': updated_value,
                            'item_id': int(single_comp_room_value.get('como_item_id'))
                            }
                        print('Process of saving composition_rooms in monday.com started>>>>>>>>>>')
                        hit_monday_api(query, variables)
                        print('Process of saving composition_rooms in monday.com ended>>>>>>>>>>')
                        break
    except Exception as e:
            print("error in update_composition_rooms::::", e)

        
def get_date_range():
    """
    Find date range to get prices of property.

    Returns:
        string: today date
        string: date after 1 year
    """
    today = date.today()
    future_date = today + relativedelta(years=1)
    return str(today), str(future_date)

def update_prices(property_id, property_name):
    """
    Update prices of single property in monday.com with single/multiple seasons.

    Args:
          property_id: The id of the property
    """

    date_from, date_to = get_date_range()
    prices_data_dicts = pull_prices_of_property_from_ru(property_id, date_from, date_to)

    pull_list = prices_data_dicts.get('Pull_ListPropertyPrices_RS')
    prices = pull_list.get('Prices')
    seasons = prices.get('Season')
    if seasons == None:
        return True

    if seasons is not None and type(seasons) != list:
        reflect_price_changes(seasons, property_id, property_name)
    else:
        for season in seasons:
            reflect_price_changes(season, property_id, property_name)

def reflect_price_changes(season, property_id, property_name):

    """
    reflect price changes of single seaosn in monday.com.

    Args:
          property_id: The id of the property
    """
    season_date_from = season.get('@DateFrom')
    season_date_to = season.get('@DateTo')
    season_price = season.get('Price')
    season_extra = season.get('Extra')

    columns = get_board_columns(int(os.getenv('PRICES_BOARD_ID')))
    query = 'mutation ($myItemName: String!, $columnVals: JSON!,$board_id:Int!,$group_id: String!) { create_item (board_id:$board_id,group_id:$group_id, item_name:$myItemName, column_values:$columnVals,create_labels_if_missing:true) { id } }'
    group = get_group_id(int(os.getenv('PRICES_BOARD_ID')))

    col_vals = json.dumps({
    # columns['rentals_united_id']: int(rental_united_id,
    columns['Property Id']: property_id,
    columns['Date From']: season_date_from,
    columns['Date To']: season_date_to,
    columns['Price']: season_price,
    columns['Extra']: season_extra
    })

    variables = {
    'board_id': int(os.getenv('PRICES_BOARD_ID')),
    'columnVals': col_vals,
    'group_id': group[0].get('id'),
    'myItemName': property_name
    }
    hit_monday_api(query, variables)

def update_amenities(property_id, list_of_amenities_of_property):
    if list_of_amenities_of_property is not None:
        amenities = list_of_amenities_of_property.get('Amenity')
        if amenities is None:
            return True
        elif type(amenities) != list:
            amenity = amenities.get('"#text"')
            reflect_amenities_change(property_id, amenity)
        else:
            for amenitie in amenities:
                amenity = amenitie.get('#text')
                reflect_amenities_change(property_id, amenity)

def reflect_amenities_change(property_id, rental_amenity_id):
    column_id = 'text2'

    items_list = get_all_group_items_of_a_single_board(int(os.getenv('AMENITIES_BOARD_ID')))
    items = items_list[0].get('items')
    for item in items:
        f_property_id = ''
        previous_property_ids, amenity_id = get_previous_property_ids(item)
        if int(rental_amenity_id) == int(amenity_id):
            if previous_property_ids is None or previous_property_ids == '':
                f_property_id = str(property_id)
            elif ',' not in previous_property_ids and str(previous_property_ids) != str(property_id):
                f_property_id = str(previous_property_ids+', '+property_id)
            elif ',' not in previous_property_ids and str(previous_property_ids) == str(property_id):
                f_property_id = ''
            elif ',' in previous_property_ids and str(property_id) not in str(previous_property_ids):
                f_property_id = str(previous_property_ids)+', '+str(property_id)
            elif ',' in previous_property_ids and str(property_id) in str(previous_property_ids):
                f_property_id = ''

            if f_property_id != '':
                print('id matched...............................', int(rental_amenity_id), amenity_id)

                # assign property_ids in column
                query = 'mutation ($board_id:Int!,$item_id:Int!,$column_id:String!,$value:String!) {change_simple_column_value (board_id:$board_id,item_id:$item_id,column_id:$column_id,value:$value,create_labels_if_missing:true) { id } }'

                variables = {
                'board_id': int(os.getenv('AMENITIES_BOARD_ID')),
                'item_id': int(item.get('id')),
                'column_id': str(column_id),
                'value': str(f_property_id)
                }
                hit_monday_api(query, variables)

def get_previous_property_ids(item):
    column_values = item.get('column_values')
    for column_value in column_values:
        if column_value.get('title') == 'Property Id':
            property_ids = column_value.get('text')
        if column_value.get('title') == 'Amenity ID':
            amenity_id = column_value.get('text')
    return property_ids, amenity_id


