from sync_rental_to_monday.monday_service import get_board_columns, get_group_id, hit_monday_api
from sync_rental_to_monday.sync_rental_united import pull_list_of_properties_from_ru, pull_min_stay_details_from_ru
import json
import os

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

            print('Process of saving values in monday.com started>>>>>>>>>>')
            hit_monday_api(query, variables)
            # update available units.
            update_avb_units(data_dict)
            # break
            print('Process of saving values in monday.com ended>>>>>>>>>>')
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

            print("-------------", [data_dict.get('property_id')])
            col_vals = json.dumps({
                columns['Name']: property.get('Name'),
                columns['Date From']: date_from,
                columns['Date To']: date_to,
                columns['Number of Units']: property.get('NoOfUnits'),
                columns['Minimum stay length']: min_stay,
                columns['Changeover type ID']: 4,
                # columns['Property IDs']: {"ids":[1]}
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
