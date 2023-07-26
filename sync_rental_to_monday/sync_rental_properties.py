from sync_rental_to_monday.monday_service import delete_all_board_data, delete_particular_column_items, get_board_columns, get_group_id, hit_monday_api, get_composition_rooms_details,get_all_group_items_of_a_single_board
from sync_rental_to_monday.sync_rental_united import pull_availability_calendar_details_from_ru, pull_list_of_properties_from_ru,pull_prices_of_property_from_ru
import json
import os
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

def sync_rental_to_monday():
    try:
        # get property_details from rental_united
        data_dicts = pull_list_of_properties_from_ru()

        print('Process of deleting data from all boards of monday.com started>>>>>>>>>>')
        # delete all the data of property board so that updated data can be inserted.
        delete_all_board_data(int(os.getenv('PROPERTIES_BOARD_ID')))
        # delete all the data of avb units board so that updated data can be inserted.
        delete_all_board_data(int(os.getenv('AVB_UNITS_BOARD_ID')))
        # delete all the data of price board so that updated data can be inserted.
        delete_all_board_data(int(os.getenv('PRICES_BOARD_ID')))
        #delete property id column of composition rooms board so that updated data can be inserted.
        delete_particular_column_items(int(os.getenv('COMP_ROOMS_BOARD_ID')), 'text')
        #delete property id column of amenities board so that updated data can be inserted.
        delete_particular_column_items(int(os.getenv('AMENITIES_BOARD_ID')), 'text2')
        print('Process of deleting data from all boards of monday.com ended>>>>>>>>>>\n')

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

            print('---------------Property_name---------------', property.get('Name'))

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

            print('Process of saving values in property board of monday.com started>>>>>>>>>>\n')
            all_property_ids = get_previous_property_ids()
            if data_dict.get('property_id') not in all_property_ids:
                hit_monday_api(query, variables)

            # update prices of property.
            print('Process of saving prices in prices board of monday.com started>>>>>>>>>>')
            all_property_data = get_previous_ids_and_dates(int(os.getenv('PRICES_BOARD_ID')), 'Property Id')
            update_prices(data_dict.get('property_id'), property.get('Name'), all_property_data)
            print('Process of saving prices in prices board of monday.com ended>>>>>>>>>>\n')

            # update available units, calendar availabilty.
            print('Process of saving avb_units, calendar in monday.com started>>>>>>>>>>')
            all_units_and_calendar_data = get_previous_ids_and_dates(int(os.getenv('AVB_UNITS_BOARD_ID')), 'Property IDs')
            add_avb_calendar_and_units(data_dict.get('property_id'), all_units_and_calendar_data, property.get('Name'))
            print('Process of saving avb_units, calendar in monday.com ended>>>>>>>>>>\n')

            # update composition rooms.
            print('Process of saving composition_rooms in monday.com started>>>>>>>>>>')
            update_composition_rooms(data_dict)
            print('Process of saving composition_rooms in monday.com ended>>>>>>>>>>\n')

            # update amenities of property.
            print('Process of saving amenities in amenities board of monday.com started>>>>>>>>>>')
            list_of_amenities_of_property = property.get('Amenities')
            update_amenities(data_dict.get('property_id'), list_of_amenities_of_property)
            print('Process of saving amenities in amenities board of monday.com ended>>>>>>>>>>\n')

        print('Process of saving values in property board of monday.com ended>>>>>>>>>>')
    except Exception as e:
        print('error in function sync_rental_to_monday', e)


def add_avb_calendar_and_units(property_id, all_monday_available_data, property_name):
    try:

        date_ranges = []
        current_start_date = None
        calendar_from = '2023-08-31'
        calendar_to = '2023-11-01'

        availability_data = pull_availability_calendar_details_from_ru(property_id, calendar_from, calendar_to)
        list_availability_data = availability_data.get('Pull_ListPropertyAvailabilityCalendar_RS')
        property_calendar = list_availability_data.get('PropertyCalendar')
        caldays = property_calendar.get('CalDay')

        if caldays is None:
            return True

        date_ranges = []
        current_start_date = None
        min_stay = None
        changeover = None

        for entry in caldays:
            date_str = entry["@Date"]
            is_blocked = entry["IsBlocked"] == "false"
            min_stay = entry["MinStay"]
            changeover = entry["Changeover"]
            avb_units = entry["@Units"]

            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

            if is_blocked:
                if not current_start_date:
                    current_start_date = date_obj
            else:
                if current_start_date:
                    date_ranges.append({
                        "start_date": current_start_date.strftime('%Y-%m-%d'),
                        "end_date": (date_obj - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
                        "min_stay": min_stay,
                        "changeover": changeover,
                        "avb_units": avb_units
                    })
                    current_start_date = None

        # Add the last range if the last date is unblocked
        if current_start_date:
            date_ranges.append({
                "start_date": current_start_date.strftime('%Y-%m-%d'),
                "end_date": date_obj.strftime('%Y-%m-%d'),
                "min_stay": min_stay,
                "changeover": changeover,
                "avb_units": avb_units
            })

        for date_range in date_ranges:
            current_tuple = (date_range.get('start_date'), date_range.get('end_date'), property_id)

            # if condition to avoid inserting duplicates.
            if current_tuple not in all_monday_available_data and date_range != []:

                columns = get_board_columns(int(os.getenv('AVB_UNITS_BOARD_ID')))
                query = 'mutation ($myItemName: String!, $columnVals: JSON!,$board_id:Int!,$group_id: String!) { create_item (board_id:$board_id,group_id:$group_id, item_name:$myItemName, column_values:$columnVals,create_labels_if_missing:true) { id } }'
                group = get_group_id(int(os.getenv('AVB_UNITS_BOARD_ID')))

                col_vals = json.dumps({
                    columns['Name']: property_name,
                    columns['Date From']: date_range.get('start_date'),
                    columns['Date To']: date_range.get('end_date'),
                    columns['Number of Units']: date_range.get('avb_units'),
                    columns['Minimum stay length']: date_range.get('min_stay'),
                    columns['Changeover type ID']: date_range.get('changeover'),
                    columns['Availability']: "Yes",
                    columns['Property IDs']: {"labels":[property_id]}
                    })
                variables = {
                    'board_id': int(os.getenv('AVB_UNITS_BOARD_ID')),
                    'columnVals': col_vals,
                    'group_id': group[0].get('id'),
                    'myItemName': property_name
                    }

                hit_monday_api(query, variables)

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
                        hit_monday_api(query, variables)
                        break
    except Exception as e:
            print("error in update_composition_rooms::::", e)


def get_date_range():
    """
    Find date range to get prices of property.

    Returns:
        string: today date
        string: date after 6 months
    """
    try:
        today = date.today()
        future_date = today + relativedelta(months=6)
        return str(today), str(future_date)
    except Exception as e:
        print('error in function get_date_range', e)

def update_prices(property_id, property_name, all_property_datas):
    """
    Update prices of single property in monday.com with single/multiple seasons.

    Args:
          property_id: The id of the property
          property_name: The name of the property
          all_property_data: The data of the property
    """

    try:
        date_from, date_to = get_date_range()

        prices_data_dicts = pull_prices_of_property_from_ru(property_id, date_from, date_to)

        pull_list = prices_data_dicts.get('Pull_ListPropertyPrices_RS')
        prices = pull_list.get('Prices')
        seasons = prices.get('Season')
        if seasons == None:
            return True

        if seasons is not None and type(seasons) != list:
            reflect_price_changes(seasons, property_id, property_name, all_property_datas)
        else:
            for season in seasons:
                reflect_price_changes(season, property_id, property_name, all_property_datas)
    except Exception as e:
        print('error in function update_prices', e)

def reflect_price_changes(season, property_id, property_name, all_property_datas):

    """
    reflect price changes of single seaosn in monday.com.

    Args:
          property_id: The id of the property
    """
    try:
        season_date_from = season.get('@DateFrom')
        season_date_to = season.get('@DateTo')
        season_price = season.get('Price')
        season_extra = season.get('Extra')

        current_price_tuple = (season_date_from, season_date_to, property_id)

        # if condition to avoid inserting duplicates.
        if current_price_tuple not in all_property_datas:
            columns = get_board_columns(int(os.getenv('PRICES_BOARD_ID')))
            query = 'mutation ($myItemName: String!, $columnVals: JSON!,$board_id:Int!,$group_id: String!) { create_item (board_id:$board_id,group_id:$group_id, item_name:$myItemName, column_values:$columnVals,create_labels_if_missing:true) { id } }'
            group = get_group_id(int(os.getenv('PRICES_BOARD_ID')))

            col_vals = json.dumps({
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

    except Exception as e:
        print('error in function reflect_price_changes', e)

def update_amenities(property_id, list_of_amenities_of_property):
    """
    update amenities in monday.com.

    Args:
          property_id: The id of the property
          list_of_amenities_of_property: list of amenities of property
    """
    try:
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

    except Exception as e:
        print('error in function update_amenities', e)

def reflect_amenities_change(property_id, rental_amenity_id):
    """
    update amenities in monday.com.

    Args:
          property_id: The id of the property
    """
    try:
        column_id = 'text2'

        items_list = get_all_group_items_of_a_single_board(int(os.getenv('AMENITIES_BOARD_ID')))
        items = items_list[0].get('items')

        if items is None:
            return True

        for item in items:
            f_property_id = ''
            previous_property_ids, amenity_id = get_property_and_amenity_ids(item)

            if int(rental_amenity_id) == int(amenity_id):
                print('----------------amenity id matched---------------', amenity_id)

                if previous_property_ids is None or previous_property_ids == '':
                    f_property_id = str(property_id)
                elif (',' not in previous_property_ids and str(previous_property_ids)) == str(property_id) or (',' in previous_property_ids and str(property_id) in str(previous_property_ids)):
                    f_property_id = ''
                elif (',' in previous_property_ids and str(property_id) not in str(previous_property_ids)) or (',' not in previous_property_ids and str(previous_property_ids) != str(property_id)):
                    f_property_id = str(previous_property_ids)+', '+str(property_id)

                if f_property_id != '':
                    # assign property_ids in column
                    query = 'mutation ($board_id:Int!,$item_id:Int!,$column_id:String!,$value:String!) {change_simple_column_value (board_id:$board_id,item_id:$item_id,column_id:$column_id,value:$value,create_labels_if_missing:true) { id } }'

                    variables = {
                    'board_id': int(os.getenv('AMENITIES_BOARD_ID')),
                    'item_id': int(item.get('id')),
                    'column_id': str(column_id),
                    'value': str(f_property_id)
                    }
                    hit_monday_api(query, variables)
                    break

    except Exception as e:
        print('error in function reflect_amenities_change', e)

def get_property_and_amenity_ids(item):
    """
    get previous properties monday.com.

    Args:
          item: single item from monday.com
    """
    try:
        column_values = item.get('column_values')
        for column_value in column_values:
            if column_value.get('title') == 'Property Id':
                property_ids = column_value.get('text')
            if column_value.get('title') == 'Amenity ID':
                amenity_id = column_value.get('text')
        return property_ids, amenity_id

    except Exception as e:
        print('error in function get_property_and_amenity_ids', e)

def get_previous_property_ids():
    """
    get previous properties ids from monday.com.

    """
    try:
        all_property_ids = []

        items_list = get_all_group_items_of_a_single_board(int(os.getenv('PROPERTIES_BOARD_ID')))
        properties = items_list[0].get('items')
        for property in properties:
                column_values = property.get('column_values')
                for column in column_values:
                    if column.get('title') == 'Property ID':
                        property_id = column.get('text')
                        all_property_ids.append(property_id)
        return all_property_ids

    except Exception as e:
        print('error in function get_previous_property_ids', e)

def get_previous_ids_and_dates(board_id, id_col_name):
    """
    get previous board ids, date_from, date_to from monday.com.

    """
    try:
        all_property_data = []

        items_list = get_all_group_items_of_a_single_board(board_id)
        properties = items_list[0].get('items')
        for property in properties:
            property_list = []
            column_values = property.get('column_values')
            for column in column_values:
                if column.get('title') == id_col_name:
                    property_list.append(column.get('text'))
                if column.get('title') == 'Date From':
                    property_list.append(column.get('text'))
                if column.get('title') == 'Date To':
                    property_list.append(column.get('text'))
            all_property_data.append(tuple(property_list))

        return all_property_data

    except Exception as e:
        print('error in function get_previous_ids_and_dates from monday', e)



