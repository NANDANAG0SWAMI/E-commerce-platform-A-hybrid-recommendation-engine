import os, requests
import base64

api_key = "notrealapisorry"
url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

with open("C:\\Users\\nanda\\OneDrive\\Pictures\\Camera Roll\\Boxplot.jpg", "rb") as img:
    b64 = base64.b64encode(img.read()).decode('utf-8')

data = {
    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "What do you see in this image?"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
        ]
    }]
}

resp = requests.post(url, headers=headers, json=data)
print(resp.json())
