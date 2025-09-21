import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Fetch the JSON data from the URL
url = "https://data.cwtv.com/feed/app-2/landing/epg/page_1/pagesize_100/device_web/apiversion_24/"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)

    # Check if response is valid JSON
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON response. This is likely due to geoblocking.")
        print("Please use a USA-based VPN to access the content and try again.")
        exit(1)

    # Extract channels
    channels = data.get('channels', [])
    if not channels:
        print("Error: No channels found in the response. The data may be incomplete or restricted.")
        print("Please ensure you're using a USA-based VPN and try again.")
        exit(1)

    # Generate XMLTV file
    root = ET.Element('tv')

    # Add channel elements
    for channel in channels:
        slug = channel.get('slug', '')
        title = channel.get('title', '')
        logo = channel.get('icon_unfocused_url', '')
        
        channel_elem = ET.SubElement(root, 'channel', id=slug)
        display_name = ET.SubElement(channel_elem, 'display-name')
        display_name.text = title
        icon = ET.SubElement(channel_elem, 'icon', src=logo)

    # Add programme elements
    for channel in channels:
        slug = channel.get('slug', '')
        for program in channel.get('programs', []):
            start_time = program.get('start_time', '')
            end_time = program.get('end_time', '')
            prog_title = program.get('title', '')
            prog_subtitle = program.get('subtitle', '')
            prog_desc = program.get('description', '')
            
            # Convert ISO times to XMLTV format (YYYYMMDDHHMMSS +0000)
            try:
                start_dt = datetime.fromisoformat(start_time.replace('+00:00', 'Z'))
                end_dt = datetime.fromisoformat(end_time.replace('+00:00', 'Z'))
                start_str = start_dt.strftime('%Y%m%d%H%M%S +0000')
                end_str = end_dt.strftime('%Y%m%d%H%M%S +0000')
            except ValueError as e:
                print(f"Warning: Skipping program with invalid time format in channel {slug}: {prog_title}")
                continue
            
            prog_elem = ET.SubElement(root, 'programme', start=start_str, stop=end_str, channel=slug)
            
            title_elem = ET.SubElement(prog_elem, 'title')
            title_elem.text = prog_title
            
            if prog_subtitle and prog_subtitle.strip():
                sub_title_elem = ET.SubElement(prog_elem, 'sub-title')
                sub_title_elem.text = prog_subtitle
            
            desc_elem = ET.SubElement(prog_elem, 'desc')
            desc_elem.text = prog_desc

    # Convert to pretty XML
    xml_str = ET.tostring(root, encoding='unicode', method='xml')
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent='  ')

    # Write to file
    with open('cwtv_epg.xml', 'w', encoding='utf-8') as xml_file:
        xml_file.write(pretty_xml)

    print("EPG exported successfully")

except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print("This is likely due to geoblocking. Please use a USA-based VPN and try again.")
except requests.exceptions.RequestException as e:
    print(f"Error: Failed to fetch data from {url}. Details: {e}")
    print("Please check your internet connection or use a USA-based VPN and try again.")
except Exception as e:
    print(f"Unexpected error: {e}")
    print("Please ensure you're using a USA-based VPN and try again.")