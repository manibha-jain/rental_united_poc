import xml.etree.ElementTree as ET
import requests
import os
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


def push_to_ru(data):
    try:
        property_data = data

        xml_payload = f"""
            <Push_PutProperty_RQ>
                <Authentication>
                    <UserName>{os.getenv('RU_USERNAME')}</UserName>
                    <Password>{os.getenv('RU_PASSWORD')}</Password>
                </Authentication>
                <Property>
                    <Name>{property_data[0]['name']}</Name>
                    <OwnerID>649371</OwnerID>
                    <DetailedLocationID TypeID="{property_data[0]['detailed_location_id']}">{property_data[0]['detailed_location']}</DetailedLocationID>
                    <IsActive>true</IsActive>
                    <IsArchived>false</IsArchived>
                    <CleaningPrice>{property_data[0]['cleaning_fee']}</CleaningPrice>
                    <Space>{property_data[0]['property_space']}</Space>
                    <StandardGuests>{property_data[0]['standard_guests']}</StandardGuests>
                    <CanSleepMax>{property_data[0]['can_sleep_max']}</CanSleepMax>
                    <PropertyTypeID>{property_data[0]['property_type_id']}</PropertyTypeID>
                    <NoOfUnits>{property_data[0]['no_of_units']}</NoOfUnits>
                    <Floor>{property_data[0]['property_floor']}</Floor>
                    <Street>{property_data[0]['street']}</Street>
                    <ZipCode>{property_data[0]['zip_code']}</ZipCode>
                    <Descriptions>
                        <Description LanguageID="1">
                            <Text>
                                {property_data[0]['description']}
                            </Text>
                        </Description>
                    </Descriptions>
                    <LicenceInfo>
                        <IsExempt>false</IsExempt>
                        <OwnerInfos />
                    </LicenceInfo>
                    <Coordinates>
                        <Longitude>{property_data[0]['longitude']}</Longitude>
                        <Latitude>{property_data[0]['latitude']}</Latitude>
                    </Coordinates>
                    <ArrivalInstructions>
                        <Landlord>{property_data[0]['landlord_name']}</Landlord>
                        <Email>{property_data[0]['landlord_email']}</Email>
                        <Phone>{property_data[0]['landlord_phone']}</Phone>
                        <DaysBeforeArrival>0</DaysBeforeArrival>
                        <PickupService />
                        <HowToArrive />
                    </ArrivalInstructions>
                    <CheckInOut>
                        <CheckInFrom>15:00</CheckInFrom>
                        <CheckInTo>23:00</CheckInTo>
                        <CheckOutUntil>10:00</CheckOutUntil>
                        <Place>at the appartment</Place>
                        <LateArrivalFees />
                        <EarlyDepartureFees />
                    </CheckInOut>
                    <PaymentMethods>
                        <PaymentMethod PaymentMethodID="1">Account number: 000000000000000</PaymentMethod>
                        <PaymentMethod PaymentMethodID="2" >VISA, MASTERCARD, AMERICAN EXPRESS</PaymentMethod>
                    </PaymentMethods>
                    <CompositionRoomsAmenities>
                    """
        for composition_room in property_data[0]['comp_rooms']:
            comp_room_id = composition_room['comp_room_id']
            room_amenities = composition_room['subitems']
            xml_payload += f'<CompositionRoomAmenities CompositionRoomID="{comp_room_id}">1\n' \
                f'    <Amenities>\n'
            for room_amenity in room_amenities:
                room_amenity_id = room_amenity['id']
                xml_payload += f'        <Amenity Count="1">{room_amenity_id}</Amenity>\n'

            xml_payload += f'    </Amenities>\n' \
                f'</CompositionRoomAmenities>\n'

        xml_payload += f'</CompositionRoomsAmenities>\n'
        xml_payload += f'<Amenities>\n'
        for amenity_id in property_data[0]['amenity_ids']:
            xml_payload += f'    <Amenity Count="1">{amenity_id}</Amenity>\n'

        xml_payload += f"""
                    </Amenities>
                    <Deposit DepositTypeID="{property_data[0]['deposit_type_id']}">{property_data[0]['deposit']}</Deposit>
                    <SecurityDeposit DepositTypeID="{property_data[0]['security_deposit_id']}">{property_data[0]['security_deposit']}</SecurityDeposit>
                    <PreparationTimeBeforeArrival>1</PreparationTimeBeforeArrival>
                    <PreparationTimeBeforeArrivalInHours>1</PreparationTimeBeforeArrivalInHours>
                    <CancellationPolicies>
                        <CancellationPolicy ValidFrom="0" ValidTo="14">100</CancellationPolicy>
                    </CancellationPolicies>
                </Property>
            </Push_PutProperty_RQ>
            """
        print(xml_payload)
        # Call the function to make the XML request
        response = make_xml_request(xml_payload)

        # Parse the XML response
        responseContent = ET.fromstring(response)
        if responseContent.find('Status') == None:
            item_ru_response= {
                'status': responseContent
            }
            return item_ru_response

        # Extract the relevant information
        status_text = responseContent.find('Status').text
        status_id = responseContent.find('Status').attrib['ID']
        response_id = responseContent.find('ResponseID').text
        ru_property_id = responseContent.find('ID').text
        # Create a list item and append the extracted values when status_id is 0
        item_ru_response = {
            'status': status_text,
            'status_id': status_id,
            'response_id': response_id
        }
        if status_id == '0':
            item_ru_response['property_id'] = ru_property_id

        # Return the list item
        return item_ru_response

        # Process the response if needed
        # print(status_text, status_id, response_id, ru_property_id)
        # Return the extracted values
        # return status_text, status_id, response_id, property_id
    except Exception as e:
        raise Exception("error in push_to_ru: " + str(e))


def update_to_ru(data, rental_property_id):
    try:
        property_data = data

        xml_payload = f"""
            <Push_PutProperty_RQ>
                <Authentication>
                    <UserName>{os.getenv('RU_USERNAME')}</UserName>
                    <Password>{os.getenv('RU_PASSWORD')}</Password>
                </Authentication>
                <Property>
                    <ID>{rental_property_id}</ID>
                    <Name>{property_data[0]['name']}</Name>
                    <OwnerID>649371</OwnerID>
                    <DetailedLocationID TypeID="{property_data[0]['detailed_location_id']}">{property_data[0]['detailed_location']}</DetailedLocationID>
                    <IsActive>true</IsActive>
                    <IsArchived>false</IsArchived>
                    <CleaningPrice>{property_data[0]['cleaning_fee']}</CleaningPrice>
                    <Space>{property_data[0]['property_space']}</Space>
                    <StandardGuests>{property_data[0]['standard_guests']}</StandardGuests>
                    <CanSleepMax>{property_data[0]['can_sleep_max']}</CanSleepMax>
                    <PropertyTypeID>{property_data[0]['property_type_id']}</PropertyTypeID>
                    <NoOfUnits>{property_data[0]['no_of_units']}</NoOfUnits>
                    <Floor>{property_data[0]['property_floor']}</Floor>
                    <Street>{property_data[0]['street']}</Street>
                    <ZipCode>{property_data[0]['zip_code']}</ZipCode>
                    <Descriptions>
                        <Description LanguageID="1">
                            <Text>
                                {property_data[0]['description']}
                            </Text>
                        </Description>
                    </Descriptions>
                    <LicenceInfo>
                        <IsExempt>false</IsExempt>
                        <OwnerInfos />
                    </LicenceInfo>
                    <Coordinates>
                        <Longitude>{property_data[0]['longitude']}</Longitude>
                        <Latitude>{property_data[0]['latitude']}</Latitude>
                    </Coordinates>
                    <ArrivalInstructions>
                        <Landlord>{property_data[0]['landlord_name']}</Landlord>
                        <Email>{property_data[0]['landlord_email']}</Email>
                        <Phone>{property_data[0]['landlord_phone']}</Phone>
                        <DaysBeforeArrival>0</DaysBeforeArrival>
                        <PickupService />
                        <HowToArrive />
                    </ArrivalInstructions>
                    <CheckInOut>
                        <CheckInFrom>15:00</CheckInFrom>
                        <CheckInTo>23:00</CheckInTo>
                        <CheckOutUntil>10:00</CheckOutUntil>
                        <Place>at the appartment</Place>
                        <LateArrivalFees />
                        <EarlyDepartureFees />
                    </CheckInOut>
                    <PaymentMethods>
                        <PaymentMethod PaymentMethodID="1">Account number: 000000000000000</PaymentMethod>
                        <PaymentMethod PaymentMethodID="2" >VISA, MASTERCARD, AMERICAN EXPRESS</PaymentMethod>
                    </PaymentMethods>
                    <CompositionRoomsAmenities>
                    """
        for composition_room in property_data[0]['comp_rooms']:
            comp_room_id = composition_room['comp_room_id']
            room_amenities = composition_room['subitems']
            xml_payload += f'<CompositionRoomAmenities CompositionRoomID="{comp_room_id}">1\n' \
                f'    <Amenities>\n'
            for room_amenity in room_amenities:
                room_amenity_id = room_amenity['id']
                xml_payload += f'        <Amenity Count="1">{room_amenity_id}</Amenity>\n'

            xml_payload += f'    </Amenities>\n' \
                f'</CompositionRoomAmenities>\n'

        xml_payload += f'</CompositionRoomsAmenities>\n'
        xml_payload += f'<Amenities>\n'
        for amenity_id in property_data[0]['amenity_ids']:
            xml_payload += f'    <Amenity Count="1">{amenity_id}</Amenity>\n'

        xml_payload += f"""
                    </Amenities>
                    <Deposit DepositTypeID="{property_data[0]['deposit_type_id']}">{property_data[0]['deposit']}</Deposit>
                    <SecurityDeposit DepositTypeID="{property_data[0]['security_deposit_id']}">{property_data[0]['security_deposit']}</SecurityDeposit>
                    <PreparationTimeBeforeArrival>1</PreparationTimeBeforeArrival>
                    <PreparationTimeBeforeArrivalInHours>1</PreparationTimeBeforeArrivalInHours>
                    <CancellationPolicies>
                        <CancellationPolicy ValidFrom="0" ValidTo="14">100</CancellationPolicy>
                    </CancellationPolicies>
                </Property>
            </Push_PutProperty_RQ>
            """
        print(xml_payload)
        # Call the function to make the XML request
        response = make_xml_request(xml_payload)

        # Parse the XML response
        responseContent = ET.fromstring(response)
        if responseContent.find('Status') == None:
            item_ru_response= {
                'status': responseContent
            }
            return item_ru_response

        # Extract the relevant information
        status_text = responseContent.find('Status').text
        status_id = responseContent.find('Status').attrib['ID']
        response_id = responseContent.find('ResponseID').text
        ru_property_id = responseContent.find('ID').text
        # Create a list item and append the extracted values when status_id is 0
        item_ru_response = {
            'status': status_text,
            'status_id': status_id,
            'response_id': response_id
        }
        if status_id == '0':
            item_ru_response['property_id'] = ru_property_id

        # Return the list item
        return item_ru_response
    except Exception as e:
        raise Exception("error in update_to_ru: " + str(e))
