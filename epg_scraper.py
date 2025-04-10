import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Simulasi data jadwal (nanti bisa diganti hasil scraping)
jadwal = [
    {
        "title": "Indonesia vs Vietnam",
        "start": datetime(2025, 6, 10, 19, 30),
        "end": datetime(2025, 6, 10, 21, 30),
        "desc": "Kualifikasi Piala Dunia"
    },
    {
        "title": "Indonesia vs Irak",
        "start": datetime(2025, 6, 15, 20, 0),
        "end": datetime(2025, 6, 15, 22, 0),
        "desc": "Friendly Match"
    }
]

tv = ET.Element('tv')
channel = ET.SubElement(tv, 'channel', id="timnas.indonesia")
ET.SubElement(channel, 'display-name').text = "Timnas Indonesia"

for match in jadwal:
    p = ET.SubElement(tv, 'programme', {
        'start': match['start'].strftime('%Y%m%d%H%M%S') + ' +0700',
        'stop': match['end'].strftime('%Y%m%d%H%M%S') + ' +0700',
        'channel': "timnas.indonesia"
    })
    ET.SubElement(p, 'title', lang="id").text = match['title']
    ET.SubElement(p, 'desc', lang="id").text = match['desc']

tree = ET.ElementTree(tv)
tree.write("epg_timnas.xml", encoding="utf-8", xml_declaration=True)
