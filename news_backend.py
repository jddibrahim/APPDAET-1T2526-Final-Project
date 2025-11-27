import math
from datetime import datetime
from iso3166 import countries
import iso639
import requests

# === SETUP DICTS FOR COUNTRIES & LANGUAGES ===
country_dict = {country.name.title(): country.alpha2.lower() for country in countries}
language_dict = {lang.name.title(): lang.part1 for lang in iso639.ALL_LANGUAGES if lang.part1}

# === API DETAILS ===
API_KEY = "47fe05de29944f4dae1a1702cd37b38b"
BASE_URL = "https://api.worldnewsapi.com/search-news"

def get_search_news_results(query: str, language=None, country=None, offset="0"):
    params = {
        "api-key": API_KEY,
        "text": f"\"{query}\"",
        "text-match-indexes": "title,content",
        "number": "5",
        "offset": offset
    }
    if language:
        params["language"] = language.lower()
    if country:
        params["source-country"] = country.lower()

    r = requests.get(BASE_URL, params=params)
    return r.json() if r.status_code == 200 else None


# =============================
# BACKEND CLASS FOR BUTTON LOGIC
# =============================
class NewsBackend:
    def __init__(self):
        self.query = None
        self.lang_code = None
        self.country_code = None
        self.total_articles = 0
        self.total_pages = 0
        self.offset = 0
        self.results = []
        self.PAGE_SIZE = 5

    # MAIN SEARCH
    def search(self, query, lang_code=None, country_code=None):
        self.query = query
        self.lang_code = lang_code
        self.country_code = country_code
        self.offset = 0

        data = get_search_news_results(query, lang_code, country_code, offset="0")
        if data is None or "news" not in data:
            self.results = []
            self.total_articles = 0
            self.total_pages = 0
            return []

        self.results = data["news"]
        self.total_articles = data.get("available", len(self.results))
        self.total_pages = max(1, math.ceil(self.total_articles / self.PAGE_SIZE))
        return self.results

    # FETCH A PAGE
    def fetch_page(self, offset):
        data = get_search_news_results(self.query, self.lang_code, self.country_code, offset=str(offset))
        if data and "news" in data:
            self.results = data["news"]
        return self.results

    # PAGINATION
    def next_page(self):
        if self.offset + self.PAGE_SIZE >= self.total_articles:
            return []
        self.offset += self.PAGE_SIZE
        return self.fetch_page(self.offset)

    def prev_page(self):
        if self.offset == 0:
            return []
        self.offset -= self.PAGE_SIZE
        return self.fetch_page(self.offset)

    def first_page(self):
        self.offset = 0
        return self.fetch_page(self.offset)

    def last_page(self):
        self.offset = (self.total_pages - 1) * self.PAGE_SIZE
        return self.fetch_page(self.offset)

    # TREND DATA
    def get_trend_data(self):
        if not self.query:
            return []

        publish_dates = []
        limit = min(self.total_articles, 50)

        for offset in range(0, limit, self.PAGE_SIZE):
            data = get_search_news_results(self.query, self.lang_code, self.country_code, offset=str(offset))
            if not data or "news" not in data:
                continue

            for entry in data["news"]:
                date_str = entry.get("publish_date")
                if not date_str:
                    continue
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    publish_dates.append(dt.date())
                except:
                    pass

        return publish_dates
