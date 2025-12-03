import requests
import json
import os
import base64
from dotenv import load_dotenv


class LineNotifier:
    def __init__(self):
        load_dotenv()
        self.channel_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.user_id = os.getenv("LINE_USER_ID")
        self.imgur_client_id = os.getenv("IMGUR_CLIENT_ID", "d29759495b6c000")

    def upload_image(self, image_path):
        if not image_path or not os.path.exists(image_path):
            print(f"Image path not found: {image_path}")
            return None

        link = self._upload_to_catbox(image_path)
        if link:
            return link

        link = self._upload_to_imgur(image_path)
        if link:
            return link

        print("All image upload methods failed")
        return None

    def _upload_to_catbox(self, image_path):
        try:
            with open(image_path, "rb") as img:
                files = {"fileToUpload": img}
                data = {"reqtype": "fileupload"}
                response = requests.post(
                    "https://catbox.moe/user/api.php",
                    files=files,
                    data=data,
                    timeout=30
                )

                if response.status_code == 200 and response.text.startswith("https://"):
                    link = response.text.strip()
                    print(f"Catbox upload successful: {link}")
                    return link
                else:
                    print(f"Catbox upload failed: {response.text}")
        except Exception as e:
            print(f"Catbox error: {e}")
        return None

    def _upload_to_imgur(self, image_path):
        url = "https://api.imgur.com/3/image"
        headers = {"Authorization": f"Client-ID {self.imgur_client_id}"}

        try:
            with open(image_path, "rb") as img:
                image_data = base64.b64encode(img.read()).decode("utf-8")
                payload = {"image": image_data, "type": "base64"}
                response = requests.post(url, headers=headers, data=payload, timeout=30)
                data = response.json()

                if data.get("success"):
                    link = data["data"]["link"]
                    print(f"Imgur upload successful: {link}")
                    return link
                else:
                    print(f"Imgur upload failed: {data.get('data', {}).get('error', 'Unknown error')}")
        except Exception as e:
            print(f"Imgur error: {e}")
        return None

    def _split_message(self, text, max_length=4900):
        if len(text) <= max_length:
            return [text]

        parts = []
        while text:
            if len(text) <= max_length:
                parts.append(text)
                break

            cut_point = text.rfind("\n", 0, max_length)
            if cut_point == -1 or cut_point < max_length // 2:
                cut_point = text.rfind(" ", 0, max_length)
            if cut_point == -1 or cut_point < max_length // 2:
                cut_point = max_length

            parts.append(text[:cut_point].strip())
            text = text[cut_point:].strip()

        return parts

    def send(self, message_text, image_paths=[]):
        if not self.channel_token or not self.user_id:
            print("Line Credentials not found.")
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.channel_token}",
        }

        text_parts = self._split_message(message_text)

        for i, text_part in enumerate(text_parts):
            messages = [{"type": "text", "text": text_part}]

            if i == len(text_parts) - 1:
                for path in image_paths:
                    img_url = self.upload_image(path)
                    if img_url:
                        messages.append(
                            {
                                "type": "image",
                                "originalContentUrl": img_url,
                                "previewImageUrl": img_url,
                            }
                        )

            payload = {"to": self.user_id, "messages": messages}

            response = requests.post(
                "https://api.line.me/v2/bot/message/push",
                headers=headers,
                data=json.dumps(payload),
            )

            if response.status_code == 200:
                print(f"Message part {i+1}/{len(text_parts)} sent successfully!")
            else:
                print(f"Failed to send message part {i+1}: {response.text}")
