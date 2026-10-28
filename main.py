import os
import random
import requests
import json
import urllib.parse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ==========================================
# 1. LUXURY TOPICS LIST
# ==========================================
LUXURY_TOPICS = [
    "Rolex Daytona Gold Edition Watch",
    "Bugatti Tourbillon Hypercar",
    "Patek Philippe Grandmaster Chime Watch",
    "Rolls-Royce Phantom Rose Gold",
    "Orient Express Venice Simplon Luxury Train",
    "Hamad International Airport Doha Al Mourjan Lounge",
    "Ducati Superleggera V4 Luxury Bike",
    "Gulfstream G700 Private Jet Luxury Interior",
    "Aston Martin DB12 Volante",
    "Singapore Changi Airport Jewel & Luxury Lounges",
    "Mercedes-Maybach S-Class Night Series",
    "Lamborghini Revuelto Hybrid Supercar",
    "Breguet Classique Complications Luxury Watch"
]

def get_random_topic():
    return random.choice(LUXURY_TOPICS)

# ==========================================
# 2. GENERATE SEO CONTENT (Using AI)
# ==========================================
def generate_article(topic):
    api_key = os.getenv("AI_API_KEY")
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Write an in-depth, high-ranking SEO blog article about '{topic}'.
    Format the entire output strictly as raw clean HTML (using <h2>, <h3>, <p>, <ul>, <li>, <strong>).
    Do NOT wrap code in markdown ```html.
    Include an eye-catching <h1> title at the start.
    Provide a detailed image generation prompt inside [IMAGE_PROMPT: description] tag at the very top.
    """
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a professional luxury blogger and SEO expert."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    return result['choices'][0]['message']['content']

# ==========================================
# 3. GENERATE PHOTO AUTOMATICALLY (Pollinations AI)
# ==========================================
def generate_image_url(image_prompt):
    encoded_prompt = urllib.parse.quote(f"hyper-realistic 8k detailed photo of {image_prompt}, cinematic lighting, luxury product photography")
    image_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){encoded_prompt}?width=1200&height=800&nologo=true&seed={random.randint(1, 999999)}"
    print(f"Generated Image URL: {image_url}")
    return image_url

# ==========================================
# 4. PUBLISH TO BLOGGER VIA API
# ==========================================
def post_to_blogger(title, content, image_url):
    blog_id = os.getenv("BLOG_ID")
    client_id = os.getenv("BLOGGER_CLIENT_ID")
    client_secret = os.getenv("BLOGGER_CLIENT_SECRET")
    refresh_token = os.getenv("BLOGGER_REFRESH_TOKEN")

    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)",
        client_id=client_id,
        client_secret=client_secret
    )

    service = build('blogger', 'v3', credentials=creds)

    full_content = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);" />
    </div>
    {content}
    """

    body = {
        "kind": "blogger#post",
        "title": title,
        "content": full_content,
        "labels": ["Luxury Lifestyle", "Supercars", "Exclusive Trends"]
    }

    posts = service.posts()
    request = posts.insert(blogId=blog_id, body=body)
    response = request.execute()
    
    print(f"Post successfully published! URL: {response.get('url')}")

# ==========================================
# MAIN EXECUTION FLOW
# ==========================================
if __name__ == "__main__":
    selected_topic = get_random_topic()
    print(f"Today's Selected Topic: {selected_topic}")

    ai_output = generate_article(selected_topic)
    
    if "[IMAGE_PROMPT:" in ai_output:
        img_prompt = ai_output.split("[IMAGE_PROMPT:")[1].split("]")[0].strip()
        html_article = ai_output.split("]", 1)[1].strip()
    else:
        img_prompt = selected_topic
        html_article = ai_output

    title = selected_topic
    if "<h1>" in html_article:
        title = html_article.split("<h1>")[1].split("</h1>")[0]
        html_article = html_article.replace(f"<h1>{title}</h1>", "")

    photo_url = generate_image_url(img_prompt)
    post_to_blogger(title, html_article, photo_url)
  
