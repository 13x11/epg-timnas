import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import re

# Daftar URL semua timnas (senior, wanita, U23, U20, U17, futsal)
TEAM_URLS = [
    "https://www.flashscore.co.id/team/indonesia/S2UCi7M9/",          # Senior
    "https://www.flashscore.co.id/team/indonesia-women/6G8FJxRj/",    # Wanita
    "https://www.flashscore.co.id/team/indonesia-u23/4kIB6Vlh/",      # U23
    "https://www.flashscore.co.id/team/indonesia-u20/COtWhKyB/",      # U20
    "https://www.flashscore.co.id/team/indonesia-u17/Kv6lAkCo/",      # U17
    "https://www.flashscore.co.id/team/indonesia-futsal/M3Fg7Nbm/"     # Futsal
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def fetch_matches(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'lxml')
        matches = []

        print(f"Jumlah elemen .event__match--scheduled di {url}: {len(soup.select('.event__match--scheduled'))}")
        for match in soup.select('.event__match--scheduled'):
            team1 = match.select_one('.event__participant--home')
            team2 = match.select_one('.event__participant--away')
            time_el = match.select_one('.event__time')
            date_header = match.find_previous('div', class_='event__round')

            if team1 and team2 and time_el:
                match_time = time_el.text.strip()
                match_date = date_header.text.strip() if date_header else ""

                # Parse tanggal (format kasar karena flashscore tidak memberi tanggal penuh)
                title = f"{team1.text.strip()} vs {team2.text.strip()}"
                desc = f"Pertandingan antara {team1.text.strip()} dan {team2.text.strip()} di {url.split('/')[-2]}"

                dt_str = match.get('id', '')
                date_match = re.search(r'match_(\d{4})(\d{2})(\d{2})', dt_str)
                if date_match:
                    year, month, day = date_match.groups()
                    start_dt = datetime.strptime(f"{year}{month}{day} {match_time}", "%Y%m%d %H:%M")
                    stop_dt = start_dt + timedelta(hours=2)

                    matches.append({
                        "title": title,
                        "desc": desc,
                        "start": start_dt,
                        "stop": stop_dt
                    })
        return matches
    except Exception as e:
        print(f"Gagal mengambil data dari {url}: {e}")
        return []


def generate_epg(matches):
    tv = ET.Element("tv")
    channel = ET.SubElement(tv, "channel", id="timnas.indonesia")
    ET.SubElement(channel, "display-name").text = "Timnas Indonesia"

    for match in sorted(matches, key=lambda x: x['start']):
        prog = ET.SubElement(tv, "programme", {
            "start": match['start'].strftime("%Y%m%dT%H%M00 +0700"),
            "stop": match['stop'].strftime("%Y%m%dT%H%M00 +0700"),
            "channel": "timnas.indonesia"
        })
        ET.SubElement(prog, "title", lang="id").text = match['title']
        ET.SubElement(prog, "desc").text = match['desc']

    tree = ET.ElementTree(tv)
    tree.write("epg_timnas.xml", encoding="utf-8", xml_declaration=True)


if __name__ == '__main__':
    all_matches = []
    for url in TEAM_URLS:
        print(f"Mengambil data dari {url}")
        all_matches.extend(fetch_matches(url))
    generate_epg(all_matches)
    print(f"Selesai. Total pertandingan ditemukan: {len(all_matches)}")
