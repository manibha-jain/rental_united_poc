import xml.etree.ElementTree as ET
import requests
import os
import xmltodict
import json
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
    pull_list = data_dict.get('Pull_ListOwnerProp_RS')
    properties = pull_list.get('Properties')
    property_list = properties.get('Property')
    print('length...', len(property_list))
    for property in property_list:
        ids = property.get('ID')
        property_id = ids.get('#text')
        data_dict = get_list_of_property_details(property_id)
        data_dict['property_id'] = property_id
        data_dicts.append(data_dict)
        # break
    return data_dicts

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




