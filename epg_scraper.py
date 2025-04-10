import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import re

# Daftar tim Timnas Indonesia di Flashscore (ID bisa berubah dari waktu ke waktu)
TEAM_URLS = {
    "Timnas Senior": "https://www.flashscore.co.id/team/indonesia/S2UCi7M9/",
    "Timnas U23": "https://www.flashscore.co.id/team/indonesia-u23/4kIB6Vlh/",
    "Timnas Wanita": "https://www.flashscore.co.id/team/indonesia-women/6G8FJxRj/",
    # Tambahan lain bisa disusulkan saat ditemukan ID-nya
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0'
}


def fetch_team_matches(team_name, url):
    matches = []
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all("script")

        # Ambil data dari script yang berisi initialStore (data embedded)
        data_script = next((s for s in scripts if 'window.main' in s.text), None)
        if not data_script:
            return matches

        raw = data_script.text
        json_raw = re.search(r'window.main\s*=\s*(\{.*?\});', raw)
        if not json_raw:
            return matches

        import json
        data = json.loads(json_raw.group(1))
        events = data.get('teams', {}).get('S2UCi7M9', {}).get('events', [])

        for event in events:
            ts = event.get('startTime')
            if not ts:
                continue
            start_dt = datetime.fromtimestamp(ts)
            if start_dt.year != 2025:
                continue
            team1 = event.get('homeTeam', {}).get('name', '')
            team2 = event.get('awayTeam', {}).get('name', '')
            title = f"{team1} vs {team2}"
            desc = event.get('tournament', {}).get('name', 'Pertandingan Timnas')

            matches.append({
                'start': start_dt,
                'stop': start_dt + timedelta(hours=2),
                'title': f"{title} ({team_name})",
                'desc': desc
            })

    except Exception as e:
        print(f"Gagal ambil data {team_name}:", e)

    return matches


def generate_epg(matches):
    tv = ET.Element("tv")
    channel = ET.SubElement(tv, "channel", id="timnas.indonesia")
    ET.SubElement(channel, "display-name").text = "Timnas Indonesia"

    for match in matches:
        programme = ET.SubElement(tv, "programme", 
            start=match['start'].strftime('%Y%m%dT%H%M%S +0700'),
            stop=match['stop'].strftime('%Y%m%dT%H%M%S +0700'),
            channel="timnas.indonesia")
        ET.SubElement(programme, "title", lang="id").text = match['title']
        ET.SubElement(programme, "desc").text = match['desc']

    tree = ET.ElementTree(tv)
    tree.write("epg_timnas.xml", encoding="utf-8", xml_declaration=True)


if __name__ == '__main__':
    all_matches = []
    for team, url in TEAM_URLS.items():
        print(f"Ambil jadwal {team}...")
        all_matches.extend(fetch_team_matches(team, url))

    print(f"Total pertandingan ditemukan: {len(all_matches)}")
    generate_epg(all_matches)
    print("Berhasil membuat epg_timnas.xml")
