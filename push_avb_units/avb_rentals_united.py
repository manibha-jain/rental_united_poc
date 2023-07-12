import xml.etree.ElementTree as ET
import requests


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

    xml_payload_1 = f"""
                    <Push_PutAvbUnits_RQ>
                    <Authentication>
                        <UserName>sid@theflexliving.com</UserName>
                        <Password>Rentals2023-</Password>
                    </Authentication>"""

    xml_payload_2 = f"""</Push_PutAvbUnits_RQ>"""
    xml_payload = xml_payload_1 + data + xml_payload_2
    print("--------xml_payload---------", xml_payload)
    # Call the function to make the XML request
    # response = make_xml_request(xml_payload)

    # # Parse the XML response
    # responseContent = ET.fromstring(response)

    # # Extract the relevant information
    # status_text = responseContent.find('Status').text
    # status_id = responseContent.find('Status').attrib['ID']
    # response_id = responseContent.find('ResponseID').text
    # ru_property_id = responseContent.find('ID').text
    # # Create a list item and append the extracted values when status_id is 0
    # item_ru_response = {
    #     'status': status_text,
    #     'status_id': status_id,
    #     'response_id': response_id
    # }
    # if status_id == '0':
    #     item_ru_response['property_id'] = ru_property_id

    # # Return the list item
    # return item_ru_response

    # Process the response if needed
    # print(status_text, status_id, response_id, ru_property_id)
    # Return the extracted values
    # return status_text, status_id, response_id, property_id
