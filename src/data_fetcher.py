import yfinance as yf
from GoogleNews import GoogleNews
import trafilatura
from urllib.parse import urlparse, parse_qs


class DataFetcher:
    def __init__(self, ticker="NVDA"):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)

    def get_stock_data(self, period="5d", interval="1h"):
        df = self.stock.history(period=period, interval=interval)
        return df

    def get_market_status(self):
        todays_data = self.stock.history(period="1d")
        last_close = todays_data["Close"].iloc[-1] if not todays_data.empty else 0

        info = self.stock.info
        current_price = info.get(
            "currentPrice", info.get("regularMarketPrice", last_close)
        )

        change_percent = (
            ((current_price - last_close) / last_close) * 100 if last_close else 0
        )

        return {
            "last_close": last_close,
            "current_price": current_price,
            "change_percent": change_percent,
        }

    def get_extended_hours_data(self):
        info = self.stock.info

        previous_close = info.get("previousClose", info.get("regularMarketPreviousClose"))

        pre_market_price = info.get("preMarketPrice")
        pre_market_change = info.get("preMarketChange")
        pre_market_change_percent = info.get("preMarketChangePercent")

        post_market_price = info.get("postMarketPrice")
        post_market_change = info.get("postMarketChange")
        post_market_change_percent = info.get("postMarketChangePercent")

        regular_market_price = info.get("regularMarketPrice")

        return {
            "previous_close": previous_close,
            "regular_market_price": regular_market_price,
            "pre_market": {
                "price": pre_market_price,
                "change": pre_market_change,
                "change_percent": pre_market_change_percent * 100 if pre_market_change_percent else None,
            },
            "post_market": {
                "price": post_market_price,
                "change": post_market_change,
                "change_percent": post_market_change_percent * 100 if post_market_change_percent else None,
            },
        }

    def get_recent_news(self, days=3):
        googlenews = GoogleNews(lang="en", region="US")
        googlenews.set_period(f"{days}d")
        googlenews.search(f"{self.ticker} stock")
        results = googlenews.result()

        news_list = []
        for news in results[:5]:
            news_list.append(f"- {news['title']} (Source: {news['media']})")

        return "\n".join(news_list)

    def clean_google_url(self, url):
        try:
            if "google.com/url" in url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                if "q" in params:
                    url = params["q"][0]

            if "&ved=" in url:
                url = url.split("&ved=")[0]
            if "&usg=" in url:
                url = url.split("&usg=")[0]

            return url
        except:
            return url

    def get_news_with_content(self, days=3, limit=5):
        print(f"Searching news for {self.ticker}...")
        googlenews = GoogleNews(lang="en", region="US")
        googlenews.set_period(f"{days}d")
        googlenews.search(f"{self.ticker} stock")
        results = googlenews.result()

        news_data = []
        count = 0

        for news in results:
            if count >= limit:
                break

            raw_url = news["link"]
            url = self.clean_google_url(raw_url)
            title = news["title"]

            print(f"Processing: {url}")

            try:
                downloaded = trafilatura.fetch_url(url)

                if downloaded:
                    content = trafilatura.extract(downloaded)

                    if content and len(content) > 100:
                        news_data.append(
                            {"title": title, "url": url, "content": content[:3000], "category": "stock"}
                        )
                        count += 1
                else:
                    print(f"Empty response from {url}")

            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                continue

        return news_data

    def get_market_news(self, days=3, limit=3):
        topics = [
            ("US economy Fed interest rates", "economy"),
            ("NASDAQ stock market", "nasdaq"),
        ]

        all_news = []

        for query, category in topics:
            print(f"Searching news for {query}...")
            googlenews = GoogleNews(lang="en", region="US")
            googlenews.set_period(f"{days}d")
            googlenews.search(query)
            results = googlenews.result()

            count = 0
            for news in results:
                if count >= limit:
                    break

                raw_url = news["link"]
                url = self.clean_google_url(raw_url)
                title = news["title"]

                print(f"Processing: {url}")

                try:
                    downloaded = trafilatura.fetch_url(url)

                    if downloaded:
                        content = trafilatura.extract(downloaded)

                        if content and len(content) > 100:
                            all_news.append(
                                {"title": title, "url": url, "content": content[:2000], "category": category}
                            )
                            count += 1
                    else:
                        print(f"Empty response from {url}")

                except Exception as e:
                    print(f"Failed to scrape {url}: {e}")
                    continue

        return all_news
