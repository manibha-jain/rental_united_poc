import xml.etree.ElementTree as ET
import requests
import os


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


def push_to_ru(formatted_string):
    xml_payload_1 = f"""
                    <Push_PutAvbUnits_RQ>
                    <Authentication>
                        <UserName>{os.getenv('RU_USERNAME')}</UserName>
                        <Password>{os.getenv('RU_PASSWORD')}</Password>
                    </Authentication>"""

    xml_payload_2 = f"""</Push_PutAvbUnits_RQ>"""
    xml_payload = xml_payload_1 + formatted_string + xml_payload_2

    # Call the function to make the XML request
    response = make_xml_request(xml_payload)
    # Parse the XML response
    responseContent = ET.fromstring(response)

    # Extract the relevant information
    status_text = responseContent.find('Status').text
    status_id = responseContent.find('Status').attrib['ID']
    response_id = responseContent.find('ResponseID').text

    item_ru_response = {
        'status': status_text,
        'status_id': status_id,
        'response_id': response_id
    }
    # Return the list item
    return item_ru_response

