
import json
import sys
from datetime import date
from pathlib import Path
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.config import get_settings
from src.utils.text import clean_text

SOURCES = [
    ("qa-student-policies", "QA Higher Education / Ulster Branch Campus Student Policies", "branch-campus policies", "https://qa.ulster.ac.uk/student-policies/"),
    ("uu-regulations", "Ulster University Ordinance and Regulations", "regulations", "https://www.ulster.ac.uk/about/ous/governance-and-policy/ordinance-and-regulations"),
    ("uu-programme-regulations", "Programme Regulations and Learning Enhancement Policies", "programme regulations", "https://www.ulster.ac.uk/learningenhancement/ccea/regulations"),
    ("uu-student-conduct", "Ulster University Student Conduct", "student conduct", "https://www.ulster.ac.uk/about/ous/student-conduct"),
    ("uu-rights", "Student Rights, Obligations and Complaints", "rights and complaints", "https://www.ulster.ac.uk/study/your-rights-and-obligations"),
]


def extract(url: str) -> str:
    response = requests.get(url, timeout=30, headers={"User-Agent": "Academic RAG prototype/1.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    main = soup.find("main") or soup.body
    return clean_text(main.get_text(" ", strip=True))


if __name__ == "__main__":
    records = []
    for source_id, title, category, url in SOURCES:
        print(f"Fetching {title}")
        records.append({
            "id": source_id,
            "title": title,
            "category": category,
            "campus_scope": "Ulster University / London branch campus",
            "url": url,
            "text": extract(url),
            "last_verified": date.today().isoformat(),
        })
    path = get_settings().raw_data_path
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved {len(records)} records to {path}")
