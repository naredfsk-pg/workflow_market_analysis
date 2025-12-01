from data_fetcher import DataFetcher
from chart_generator import ChartGenerator
from llm_analyzer import LLMAnalyzer
from line_notifier import LineNotifier
import os


def main():
    print("🚀 Starting NVDA Advanced Analysis...")

    fetcher = DataFetcher("NVDA")
    df_1d = fetcher.get_stock_data(period="1d", interval="5m")
    df_5d = fetcher.get_stock_data(period="5d", interval="1h")

    market_status = fetcher.get_market_status()

    raw_news = fetcher.get_news_with_content(limit=5)

    chart_gen = ChartGenerator()
    path_1d = chart_gen.generate_chart(df_1d, "nvda_1d.png", "NVDA 1 Day (5m)")
    path_5d = chart_gen.generate_chart(df_5d, "nvda_5d.png", "NVDA 5 Days (1h)")

    try:
        analyzer = LLMAnalyzer()

        if raw_news:
            news_summary = analyzer.summarize_news(raw_news)
        else:
            news_summary = "ไม่มีข่าวสำคัญในช่วง 3 วันที่ผ่านมา"

        print("News Summarized:\n", news_summary)
        print("-" * 100)

        analysis_result = analyzer.analyze(
            market_status, news_summary, [path_1d, path_5d]
        )
        print("Final Analysis Complete.")
        print("-" * 100)

    except Exception as e:
        analysis_result = f"Error during analysis: {str(e)}"
        print(analysis_result)

    print("📱 Sending to Line...")
    notifier = LineNotifier()

    final_message = f"🔥 NVDA Strategic Plan 🔥\n\n{analysis_result}"

    notifier.send(final_message, [path_1d, path_5d])
    print("Done!")


if __name__ == "__main__":
    main()
