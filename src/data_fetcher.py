import yfinance as yf
from GoogleNews import GoogleNews
import pandas as pd
from datetime import datetime, timedelta
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
        """ล้าง Tracking Params ของ Google ออกจาก URL"""
        try:
            # กรณี 1: เป็น Link redirect ของ google (google.com/url?q=...)
            if "google.com/url" in url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                if "q" in params:
                    url = params["q"][0]

            # กรณี 2: มี params &ved, &usg ต่อท้าย (เหมือนใน log ของคุณ)
            # ตัดทิ้งตั้งแต่เครื่องหมาย & ตัวแรกที่เจอหลังจากจบ URL ปกติ
            # วิธีบ้านๆ แต่ได้ผลคือ split เอาแค่ส่วนหน้า
            if "&ved=" in url:
                url = url.split("&ved=")[0]
            if "&usg=" in url:
                url = url.split("&usg=")[0]

            return url
        except:
            return url

    def get_news_with_content(self, days=3, limit=5):
        print(f"🕵️‍♂️ Searching news for {self.ticker}...")
        googlenews = GoogleNews(lang="en", region="US")
        googlenews.set_period(f"{days}d")
        # encode=True ช่วยเรื่องภาษาแปลกๆ ได้บ้าง แต่ถ้า Error บ่อยลองเอาออกได้
        googlenews.search(f"{self.ticker} stock")
        results = googlenews.result()

        news_data = []
        count = 0

        for news in results:
            if count >= limit:
                break

            # --- เรียกใช้ฟังก์ชันล้างลิงก์ตรงนี้ ---
            raw_url = news["link"]
            url = self.clean_google_url(raw_url)
            # ----------------------------------

            title = news["title"]

            print(f"Processing: {url}")  # Print ดูว่าลิงก์สะอาดหรือยัง

            try:
                # เพิ่ม config ให้ trafilatura เนียนขึ้น
                downloaded = trafilatura.fetch_url(url)

                if downloaded:
                    content = trafilatura.extract(downloaded)

                    if content and len(content) > 100:
                        news_data.append(
                            {"title": title, "url": url, "content": content[:3000]}
                        )
                        count += 1
                else:
                    print(f"Empty response from {url}")

            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                continue

        return news_data
