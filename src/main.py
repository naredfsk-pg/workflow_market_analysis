from data_fetcher import DataFetcher
from chart_generator import ChartGenerator
from llm_analyzer import LLMAnalyzer
from line_notifier import LineNotifier
from market_schedule import MarketSchedule
from datetime import datetime, timezone, timedelta


def main():
    schedule = MarketSchedule()
    if not schedule.is_trading_day():
        print("Today is not a trading day. Skipping analysis.")
        return

    print("Starting NVDA Advanced Analysis...")

    th_tz = timezone(timedelta(hours=7))
    now = datetime.now(th_tz)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    fetcher = DataFetcher("NVDA")
    df_1d = fetcher.get_stock_data(period="1d", interval="5m")
    df_5d = fetcher.get_stock_data(period="5d", interval="1h")

    market_status = fetcher.get_market_status()
    extended_hours = fetcher.get_extended_hours_data()

    raw_news = fetcher.get_news_with_content(limit=5)
    market_news = fetcher.get_market_news(limit=3)

    chart_gen = ChartGenerator()
    path_1d = chart_gen.generate_chart(df_1d, "nvda_1d.png", "NVDA 1 Day (5m)")
    path_5d = chart_gen.generate_chart(df_5d, "nvda_5d.png", "NVDA 5 Days (1h)")

    news_summary = "ไม่มีข่าวสำคัญในช่วง 3 วันที่ผ่านมา"
    analysis_result = "ไม่สามารถวิเคราะห์ได้"

    try:
        analyzer = LLMAnalyzer()

        all_news = raw_news + market_news
        if all_news:
            try:
                news_summary = analyzer.summarize_news(all_news)
            except Exception as e:
                print(f"Error summarizing news: {e}")
                news_summary = "ไม่สามารถสรุปข่าวได้"

        print("News Summarized:\n", news_summary)
        print("-" * 100)

        analysis_result = analyzer.analyze(
            market_status, extended_hours, news_summary, [path_1d, path_5d]
        )
        print("Final Analysis Complete.")
        print("-" * 100)

    except Exception as e:
        print(f"Error during analysis: {e}")

    print("Sending to Line...")
    notifier = LineNotifier()

    final_message = (
        f"NVDA Strategic Plan\n{date_str} {time_str}\n\n{analysis_result}"
    )

    news_summary = f"{date_str} {time_str}\nNews Summary:\n\n{news_summary}"

    notifier.send(news_summary)
    notifier.send(final_message, [path_1d, path_5d])
    print("Done!")


if __name__ == "__main__":
    main()
