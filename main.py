import os
import random
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
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Write an in-depth, high-ranking SEO blog article about {topic}.
    Format the entire output strictly as raw clean HTML (using <h2>, <p> etc.). 
    Do NOT wrap code in markdown. 
    Include an eye-catching <h1> title at the start, followed by '---' on the next line, and then the rest as the HTML body content.
    """
    
    response = model.generate_content(prompt)
    return response.text

# 3. SEND POST TO BLOGGER VIA EMAIL
def send_email_to_blogger(content_text):
    blogger_email = os.environ.get("BLOGGER_EMAIL")
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")

    # Title और Body को अलग करना
    parts = content_text.split('---', 1)
    blog_title = parts[0].strip() if len(parts) > 1 else "Luxury Lifestyle Post"
    blog_body = parts[1].strip() if len(parts) > 1 else content_text

    print(f"Generated Title: {blog_title}")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = blogger_email
    msg['Subject'] = blog_title
    msg.attach(MIMEText(blog_body, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, blogger_email, msg.as_string())
        server.quit()
        print("Blog post email sent successfully to Blogger!")
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    topic = get_random_topic()
    print(f"Selected Topic: {topic}")
    article = generate_article(topic)
    send_email_to_blogger(article)
