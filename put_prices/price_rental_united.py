import requests
import xml.etree.ElementTree as ET
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


def push_to_ru(data):
    property_data = data

    xml_payload = f"""<Push_PutPrices_RQ>
                        <Authentication>
                            <UserName>{os.getenv('RU_USERNAME')}</UserName>
                            <Password>{os.getenv('RU_PASSWORD')}</Password>
                        </Authentication>
                        <Prices PropertyID="{property_data['property_id']}">
                            <Season DateFrom="{property_data['date_from']}" DateTo="{property_data['date_to']}">
                            <Price>{property_data['price']}</Price>
                            <Extra>{property_data['extra']}</Extra>
                            </Season>
                        </Prices>
                    </Push_PutPrices_RQ>"""

    # Call the function to make the XML request
    response = make_xml_request(xml_payload)

    # Parse the XML response
    responseContent = ET.fromstring(response)

    # Extract the relevant information
    status_text = responseContent.find('Status').text
    status_id = responseContent.find('Status').attrib['ID']
    response_id = responseContent.find('ResponseID').text

    # Create a list item and append the extracted values when status_id is 0
    item_ru_response = {
        'status': status_text,
        'status_id': status_id,
        'response_id': response_id
    }

    # Return the list item
    return item_ru_response