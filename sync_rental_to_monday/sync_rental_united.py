import requests
import os
import xmltodict
from dotenv import load_dotenv
load_dotenv()

def make_xml_request(xml_payload):
    # Replace with the actual URL for sending the XML request
    url = 'http://new.rentalsunited.com/api/handler.ashx'

    headers = {
        'Content-Type': 'application/xml'
    }

    try:
        response = requests.post(url, data=xml_payload, headers=headers)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error sending XML request: {str(e)}")
        return None

def pull_list_of_properties_from_ru():
    try:
        data_dicts = []

        xml_payload = f"""
                        <Pull_ListOwnerProp_RQ>
                        <Authentication>
                        <UserName>{os.getenv('RU_USERNAME')}</UserName>
                        <Password>{os.getenv('RU_PASSWORD')}</Password>
                        </Authentication>
                        <Username>sid@theflexliving.com</Username>
                        <IncludeNLA>false</IncludeNLA>
                        </Pull_ListOwnerProp_RQ>
                    """
        # Call the function to make the XML request
        response = make_xml_request(xml_payload)
        data_dict = xmltodict.parse(response)
        if 'error' in list(data_dict.keys()):
            raise Exception("error while fetching rentals united data")

        pull_list = data_dict.get('Pull_ListOwnerProp_RS')
        properties = pull_list.get('Properties')
        property_list = properties.get('Property')

        for property in property_list:
            ids = property.get('ID')
            property_id = ids.get('#text')
            data_dict = get_list_of_property_details(property_id)
            data_dict['property_id'] = property_id
            data_dicts.append(data_dict)

        return data_dicts
    except Exception as e:
        raise Exception("error in pull_list_of_properties_from_ru: " + str(e))

def pull_prices_of_property_from_ru(property_id, date_from, date_to):
    print('property_id...........', property_id)

    xml_payload = f"""
                    <Pull_ListPropertyPrices_RQ>
                <Authentication>
                    <UserName>{os.getenv('RU_USERNAME')}</UserName>
                    <Password>{os.getenv('RU_PASSWORD')}</Password>
                </Authentication>
                <PropertyID>{property_id}</PropertyID>
                <DateFrom>{date_from}</DateFrom>
                <DateTo>{date_to}</DateTo>
            </Pull_ListPropertyPrices_RQ>
                """
    # Call the function to make the XML request
    response = make_xml_request(xml_payload)
    data_dict = xmltodict.parse(response)
    return data_dict

def get_list_of_property_details(property_id):
    xml_payload = f"""
                    <Pull_ListSpecProp_RQ>
                    <Authentication>
                    <UserName>{os.getenv('RU_USERNAME')}</UserName>
                    <Password>{os.getenv('RU_PASSWORD')}</Password>
                    </Authentication>
                    <PropertyID>{property_id}</PropertyID>
                    </Pull_ListSpecProp_RQ>
                """

    # Call the function to make the XML request
    response = make_xml_request(xml_payload)
    data_dict = xmltodict.parse(response)
    return data_dict


def pull_list_of_calendar_days(property_id, date_from, date_to):
    xml_payload = f"""
                    <Pull_ListPropertyAvailabilityCalendar_RQ>
                    <Authentication>
                        <UserName>{os.getenv('RU_USERNAME')}</UserName>
                        <Password>{os.getenv('RU_PASSWORD')}</Password>
                    </Authentication>
                    <PropertyID>{property_id}</PropertyID>
                    <DateFrom>{date_from}</DateFrom>
                    <DateTo>{date_to}</DateTo>
                    </Pull_ListPropertyAvailabilityCalendar_RQ>
                """
    # Call the function to make the XML request
    response = make_xml_request(xml_payload)
    data_dict = xmltodict.parse(response)
    return data_dict

def pull_min_stay_details_from_ru(property_id):
    xml_payload = f"""
                        <Pull_ListPropertyMinStay_RQ>
                            <Authentication>
                                <UserName>{os.getenv('RU_USERNAME')}</UserName>
                                <Password>{os.getenv('RU_PASSWORD')}</Password>
                            </Authentication>
                            <PropertyID>{property_id}</PropertyID>
                            <DateFrom>2023-07-01</DateFrom>
                            <DateTo>2023-08-30</DateTo>
                        </Pull_ListPropertyMinStay_RQ>
                    """
    # Call the function to make the XML request
    response = make_xml_request(xml_payload)
    data_dict = xmltodict.parse(response)
    return data_dict




