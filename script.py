"""
Fetches https://www.meteo.cat/ and saves the table(s) inside the element
with id="resumSM" into a CSV named with today's date (YYYY-MM-DD.csv).
"""

import csv
import os
import sys
from datetime import date

import requests
from bs4 import BeautifulSoup

URL = "https://www.meteo.cat/"

# meteo.cat can reject requests with no/odd User-Agent, so pretend to be a browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def main() -> None:
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    container = soup.find(id="resumSM")

    if container is None:
        print(
            "Could not find any element with id='resumSM'. "
            "The page structure may have changed, or the id lives on content "
            "that is only injected client-side via JavaScript (requests won't "
            "see that).",
            file=sys.stderr,
        )
        sys.exit(1)

    tables = container.find_all("table")
    if not tables:
        print(
            "Found the 'resumSM' element but it contains no <table> tags.",
            file=sys.stderr,
        )
        sys.exit(1)

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)

    today = date.today().isoformat()  # e.g. 2026-07-08
    filename = os.path.join(output_dir, f"{today}.csv")

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["table_index", "caption", "col1", "col2", "col3"])

        for i, table in enumerate(tables):
            caption_tag = table.find("caption")
            caption = caption_tag.get_text(strip=True) if caption_tag else ""

            for row in table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                if not cells:
                    continue
                # pad/truncate to 3 columns since some tables have 2 (name, value)
                # and others 3 (name, direction, value)
                cells = (cells + ["", "", ""])[:3]
                writer.writerow([i, caption] + cells)

    print(f"Saved {filename} ({sum(len(t.find_all('tr')) for t in tables)} rows across {len(tables)} table(s))")


if __name__ == "__main__":
    main()