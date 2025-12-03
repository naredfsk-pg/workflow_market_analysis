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
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def summarize_news(self, news_items):
        print("Summarizing news contents...")

        raw_text = ""
        for i, news in enumerate(news_items):
            category = news.get("category", "stock")
            raw_text += f"News {i+1} [{category.upper()}]: {news['title']}\nContent: {news['content']}\n\n"

        summary_prompt = f"""
        Role: Senior Financial News Editor
        Task: Read the following {len(news_items)} news articles and summarize them.

        News Categories:
        - STOCK: ข่าวเกี่ยวกับ NVDA โดยตรง
        - ECONOMY: ข่าวเศรษฐกิจสหรัฐ (Fed, Interest Rates, Inflation)
        - NASDAQ: ข่าวตลาด NASDAQ และ Tech Sector

        Constraints:
        1. Focus ONLY on factors affecting NVDA stock price.
        2. For ECONOMY news: Focus on Fed policy, interest rates, inflation that could impact tech stocks.
        3. For NASDAQ news: Focus on overall tech sector trends.
        4. Extract hard numbers if available (Revenue, Price Target, % Growth, Interest Rates).
        5. Detect Sentiment (Positive/Negative) for each news.

        Input News:
        {raw_text}

        Output Format (Strictly follow this pattern, group by category):

        NVDA News:
        idx. [Title]
           - Summary: [Your sharp summary in Thai language]

        US Economy:
        idx. [Title]
           - Summary: [Your sharp summary in Thai language]

        NASDAQ/Tech Sector:
        idx. [Title]
           - Summary: [Your sharp summary in Thai language]
        """

        response = self.model.generate_content(
            summary_prompt,
            safety_settings=self.safety_settings
        )
        return self._get_response_text(response)

    def _get_response_text(self, response):
        try:
            return response.text
        except ValueError:
            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    return candidate.content.parts[0].text
            return "ไม่สามารถสร้างข้อความได้"

    def analyze(self, market_data, extended_hours, summarized_news, image_paths):
        print("Generating final analysis...")

        pre_market_info = ""
        if extended_hours["pre_market"]["price"]:
            pre_market_info = f"""
        Pre-Market:
        - ราคา Pre-market: {extended_hours['pre_market']['price']:.2f}
        - การเปลี่ยนแปลง: {extended_hours['pre_market']['change']:.2f} ({extended_hours['pre_market']['change_percent']:.2f}%)"""

        post_market_info = ""
        if extended_hours["post_market"]["price"]:
            post_market_info = f"""
        After Hours (Post-Market):
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

        response = self.model.generate_content(
            contents,
            safety_settings=self.safety_settings
        )
        return self._get_response_text(response)
