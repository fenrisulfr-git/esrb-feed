import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
# Pages to scrape
PAGES = {
    "Research": "https://www.esrb.europa.eu/pub/rd/html/index.en.html",
    "NBFI Monitor": "https://www.esrb.europa.eu/pub/reports/nbfi_monitor/html/index.en.html",
    "Macroprudential Review": "https://www.esrb.europa.eu/pub/reports/review_macroprudential_policy/html/index.en.html",
    "Recommendations": "https://www.esrb.europa.eu/mppa/recommendations/html/index.en.html",
    "Opinions": "https://www.esrb.europa.eu/mppa/opinions/html/index.en.html",
    "Stress Tests": "https://www.esrb.europa.eu/mppa/stress/html/index.en.html",
    "Framework": "https://www.esrb.europa.eu/mppa/framework/html/index.en.html",
    "Responses": "https://www.esrb.europa.eu/mppa/responses/html/index.en.html",
    "Annual Reports": "https://www.esrb.europa.eu/pub/reports/ar/html/index.en.html",
    "Advisory Scientific Committee": "https://www.esrb.europa.eu/pub/asc/html/index.en.html",
    "Series": "https://www.esrb.europa.eu/pub/series/html/index.en.html",
    "Press Releases": "https://www.esrb.europa.eu/news/pr/html/index.en.html",
    "Schedule": "https://www.esrb.europa.eu/news/schedule/html/index.en.html",
    "EC": "https://commission.europa.eu/news-and-media/news_en?page=1",
    "ECB": "https://www.ecb.europa.eu/press/pubbydate/html/index.en.html"
}
# Extract items from one page
def extract_items(url, source_name):
    items = []
    try:
        res = requests.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for link in soup.select("div.box_list a"):
            title = link.get_text(strip=True)
            href = link.get("href")
            if not title or not href:
                continue
            full_link = requests.compat.urljoin(url, href)
            items.append((f"{source_name}: {title}", full_link))
    except Exception as e:
        print(f"Failed to fetch {source_name}: {e}")
    return items
# Aggregate and format all items
rss_items = []
for name, url in PAGES.items():
    rss_items += extract_items(url, name)
rss_items = rss_items[:50]  # Limit to 50 items
# Build RSS XML
rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "ESRB Combined Feed"
ET.SubElement(channel, "link").text = "https://www.esrb.europa.eu"
ET.SubElement(channel, "description").text = "Combined updates from ESRB publications and news pages"
ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
for title, link in rss_items:
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "link").text = link
    ET.SubElement(item, "description").text = title
    ET.SubElement(item, "pubDate").text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
    ET.SubElement(item, "guid").text = link
tree = ET.ElementTree(rss)
tree.write("combined.xml", encoding="utf-8", xml_declaration=True)
