import google.generativeai as genai
import os
from dotenv import load_dotenv


class LLMAnalyzer:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def summarize_news(self, news_items):

        print("Summarizing news contents...")

        raw_text = ""
        for i, news in enumerate(news_items):
            raw_text += f"News {i+1}: {news['title']}\nContent: {news['content']}\n\n"

        summary_prompt = f"""
        Role: Senior Financial News Editor
        Task: Read the following {len(news_items)} news articles about NVDA and summarize them.
        
        Constraints:
        1. Focus ONLY on factors affecting stock price (Earnings, Competitors, Analyst Ratings, Macroeconomics).
        2. Ignore general fluff or intro/outro text.
        3. Extract hard numbers if available (Revenue, Price Target, % Growth).
        4. Detect Sentiment (Positive/Negative) for each news.
        
        Input News:
        {raw_text}
        
        Output Format (Strictly follow this pattern for each news):
        idx. [Title]
           - Summary: [Your sharp summary in Thai language]
        """

        response = self.model.generate_content(summary_prompt)
        return response.text

    def analyze(self, market_data, extended_hours, summarized_news, image_paths):
        print("Generating final analysis...")

        # สร้างข้อความ Pre-market
        pre_market_info = ""
        if extended_hours["pre_market"]["price"]:
            pre_market_info = f"""
        📈 Pre-Market:
        - ราคา Pre-market: {extended_hours['pre_market']['price']:.2f}
        - การเปลี่ยนแปลง: {extended_hours['pre_market']['change']:.2f} ({extended_hours['pre_market']['change_percent']:.2f}%)"""

        # สร้างข้อความ Post-market (After Hours)
        post_market_info = ""
        if extended_hours["post_market"]["price"]:
            post_market_info = f"""
        🌙 After Hours (Post-Market):
        - ราคา After Hours: {extended_hours['post_market']['price']:.2f}
        - การเปลี่ยนแปลง: {extended_hours['post_market']['change']:.2f} ({extended_hours['post_market']['change_percent']:.2f}%)"""

        prompt = f"""
        Role: คุณคือ AI Financial Analyst ผู้เชี่ยวชาญด้าน Technical Analysis และ Options Trading
        Task: วิเคราะห์หุ้น NVDA

        Market Context:
        - ราคาปิดล่าสุด (Previous Close): {market_data['last_close']:.2f}
        - ราคาปัจจุบัน (Regular Market): {market_data['current_price']:.2f}
        - การเปลี่ยนแปลง: {market_data['change_percent']:.2f}%
        {pre_market_info}
        {post_market_info}

        Recent News (Analyzed):
        {summarized_news}

        คำสั่ง:
        วิเคราะห์จากกราฟที่แนบมา (1 Day และ 5 Days) และข้อมูลข้างต้น เพื่อตอบคำถาม 2 ข้อนี้ (ภาษาไทย):

        สำคัญ: หากมีข้อมูล Pre-market หรือ After Hours ให้นำมาวิเคราะห์ด้วย เพราะเป็นสัญญาณที่บ่งบอกทิศทางของตลาดก่อนเปิด

        1. แผนการเล่น Option (ระยะสั้น < 7 วัน):
           - แนวโน้ม (Bullish/Bearish) พร้อมอธิบายเหตุผลจาก Pre-market/After Hours (ถ้ามี)
           - ควรเข้าสถานะ (CALL/PUT) ที่ Strike Price เท่าไหร่
           - จุดเข้า (Entry) และ จุดออก (Exit/Stop Loss)

        2. แผนการลงทุนระยะยาว (DCA):
           - ควรซื้อเพิ่มตอนนี้เลยหรือไม่ หรือควรรอแนวรับที่เท่าไหร่

        Format: ขอแบบกระชับ อ่านง่าย เหมาะสำหรับส่งไลน์
        """

        contents = [prompt]
        for img_path in image_paths:
            if img_path:
                contents.append(genai.upload_file(img_path))

        response = self.model.generate_content(contents)
        return response.text
