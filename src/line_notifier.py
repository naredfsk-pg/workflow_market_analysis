import requests
import json
import os
from dotenv import load_dotenv


class LineNotifier:
    def __init__(self):
        load_dotenv()
        self.channel_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.user_id = os.getenv("LINE_USER_ID")
        self.imgur_client_id = "d29759495b6c000"

    def upload_image(self, image_path):
        if not image_path or not os.path.exists(image_path):
            return None

        url = "https://api.imgur.com/3/image"
        headers = {"Authorization": f"Client-ID {self.imgur_client_id}"}

        try:
            with open(image_path, "rb") as img:
                payload = {"image": img.read()}
                response = requests.post(url, headers=headers, data=payload)
                data = response.json()
                if data["success"]:
                    return data["data"]["link"]
        except Exception as e:
            print(f"Error uploading image: {e}")
        return None

    def send(self, message_text, image_paths=[]):
        if not self.channel_token or not self.user_id:
            print("Line Credentials not found.")
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.channel_token}",
        }

        messages = []

        messages.append({"type": "text", "text": message_text})

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
            print("Message sent successfully!")
        else:
            print(f"Failed to send message: {response.text}")
