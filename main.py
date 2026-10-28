import os
import random
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai

# 1. LUXURY TOPICS LIST
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

# 2. GENERATE CONTENT USING GEMINI AI
def generate_article(topic):
    api_key = os.environ.get("AI_API_KEY")
    if not api_key:
        raise ValueError("Error: AI_API_KEY environment variable set nahi hai!")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt ko saaf format me rakha gaya hai
    prompt = f"""
    Write an in-depth, high-ranking SEO blog article about: {topic}.
    Format the output as follows:
    LINE 1: The blog title in plain text (no HTML, no asterisks, no quotes).
    LINE 2: ---
    LINE 3 ONWARDS: The full blog post body in clean HTML (using <h2>, <h3>, <p>, <ul>, <li>).
    Do NOT include <h1> in the body. Do NOT wrap output in markdown codeblocks (no ```html).
    """
    
    response = model.generate_content(prompt)
    return response.text

# 3. SEND POST TO BLOGGER VIA EMAIL
def send_email_to_blogger(content_text):
    blogger_email = os.environ.get("BLOGGER_EMAIL")
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")

    if not all([blogger_email, sender_email, sender_password]):
        raise ValueError("Error: Email credentials (BLOGGER_EMAIL, SENDER_EMAIL, ya SENDER_PASSWORD) missing hain!")

    # AI agar markdown (```html) laga de toh use hatayein
    cleaned_text = re.sub(r"^```[a-zA-Z]*\n", "", content_text.strip())
    cleaned_text = re.sub(r"\n```$", "", cleaned_text.strip())

    # Title aur Body alag karein
    if '---' in cleaned_text:
        parts = cleaned_text.split('---', 1)
        raw_title = parts[0].strip()
        blog_body = parts[1].strip()
    else:
        raw_title = "Luxury Lifestyle Post"
        blog_body = cleaned_text

    # Title se HTML tags aur Newlines hatayein (taki email header crash na ho)
    blog_title = re.sub(r'<[^>]*>', '', raw_title)
    blog_title = " ".join(blog_title.splitlines()).strip()

    print(f"Cleaned Title: {blog_title}")

    # Email message banayein
    msg = MIMEMultipart("alternative")
    msg['From'] = sender_email
    msg['To'] = blogger_email
    msg['Subject'] = blog_title

    # HTML Body attach karein
    msg.attach(MIMEText(blog_body, 'html', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, blogger_email, msg.as_string())
        server.quit()
        print("✅ Blog post email sent successfully to Blogger!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    topic = get_random_topic()
    print(f"Selected Topic: {topic}")
    
    try:
        article = generate_article(topic)
        send_email_to_blogger(article)
    except Exception as e:
        print(f"Execution Error: {e}")
