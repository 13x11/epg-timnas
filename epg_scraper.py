import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Daftar URL timnas Indonesia berbagai kategori
teams = {
    "timnas_senior": {
        "url": "https://www.flashscore.co.id/tim/indonesia/88ErHiT9/jadwal-pertandingan/",
        "name": "Timnas Indonesia"
    },
    "timnas_u23": {
        "url": "https://www.flashscore.co.id/tim/indonesia/l4Lvnhnt/jadwal-pertandingan/",
        "name": "Timnas Indonesia U23"
    },
    "timnas_u20": {
        "url": "https://www.flashscore.co.id/tim/indonesia/vLSZTFB1/jadwal-pertandingan/",
        "name": "Timnas Indonesia U20"
    },
    "timnas_u17": {
        "url": "https://www.flashscore.co.id/tim/indonesia/xbitqDLS/jadwal-pertandingan/",
        "name": "Timnas Indonesia U17"
    },
    "timnas_wanita": {
        "url": "https://www.flashscore.co.id/tim/indonesia/v7QFt446/jadwal-pertandingan/",
        "name": "Timnas Indonesia Wanita"
    },
    "timnas_futsal": {
        "url": "https://www.flashscore.co.id/tim/indonesia/vsQkbay2/jadwal-pertandingan/",
        "name": "Timnas Indonesia Futsal"
    }
}

def get_schedule(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    matches = []

    for match in soup.select(".event__match"):
        try:
            date_str = match.select_one(".event__time").text.strip()
            opponent = match.select_one(".event__participant--away").text.strip()
            competition = match.select_one(".event__title--name").text.strip()
            match_time = datetime.strptime(date_str, "%d.%m. %H:%M")
            match_time = match_time.replace(year=datetime.now().year)

            matches.append({
                "title": opponent,
                "start": match_time,
                "end": match_time + timedelta(hours=2),
                "desc": competition
            })
        except:
            continue

    return matches

# Membuat struktur XMLTV
tv = ET.Element('tv')

for key, team in teams.items():
    channel_id = key
    channel = ET.SubElement(tv, 'channel', id=channel_id)
    ET.SubElement(channel, 'display-name').text = team['name']

    matches = get_schedule(team['url'])
    for match in matches:
        p = ET.SubElement(tv, 'programme', {
            'start': match['start'].strftime('%Y%m%d%H%M%S') + ' +0700',
            'stop': match['end'].strftime('%Y%m%d%H%M%S') + ' +0700',
            'channel': channel_id
        })
        ET.SubElement(p, 'title', lang="id").text = f"{team['name']} vs {match['title']}"
        ET.SubElement(p, 'desc', lang="id").text = match['desc']

# Simpan file XML
tree = ET.ElementTree(tv)
tree.write("epg_timnas.xml", encoding="utf-8", xml_declaration=True)
