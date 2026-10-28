import os
import random
import smtplib
import urllib.parse
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import google.generativeai as genai

# लक्ज़री कैटेगरी ताकि हर दिन अलग-अलग चीज़ों पर पोस्ट बने
CATEGORIES = [
    "Ultra-Luxury Hypercar or Supercar",
    "Haute Horlogerie / Rare Luxury Watch",
    "Private Jet or Ultra-Luxury Supersonic Aircraft",
    "Megayacht or Superyacht Interior & Design",
    "Ultra-Luxury Concept Bike or Superbike",
    "World's Most Luxurious Train Journey or First-Class Flight Cabin",
    "Multi-Million Dollar Luxury Villa or Penthouse Architecture"
]

def generate_luxury_article():
    api_key = os.environ.get("AI_API_KEY")
    genai.configure(api_key=api_key)
    
    # gemini-1.5-flash या gemini-1.5-pro
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    selected_category = random.choice(CATEGORIES)
    
    prompt = f"""
    You are an elite luxury lifestyle journalist and master SEO copywriter.
    Pick a specific, trending, or iconic subject in this category: '{selected_category}'.
    
    Requirements:
    1. Title: Create an ultra-clickable, high-CTR SEO title (NO HTML in title).
    2. Image Prompt: Write a 10-15 word realistic, 8K hyper-detailed photorealistic prompt to generate an HD image of this subject.
    3. Article: An in-depth, mobile-friendly SEO article (800-1200 words).
       - Include <h2>, <h3>, bullet points, technical specs, pricing, and FAQs.
       - Mobile responsive: keep paragraphs short (2-3 sentences max).
    
    STRICT OUTPUT FORMAT:
    TITLE: [Put title here]
    IMAGE_PROMPT: [Put 10-15 word image prompt here]
    CONTENT:
    [Put raw HTML content here starting directly with <h2> or <p>. Do not include <html> or <body> tags. Do not use Markdown code blocks like ```html]
    """
    
    response = model.generate_content(prompt)
    return response.text

def parse_and_build_html(raw_text):
    # Markdown backticks हटाना अगर AI जोड़ दे
    clean_text = raw_text.replace("```html", "").replace("```", "").strip()
    
    # Title निकालना
    title_match = re.search(r"TITLE:\s*(.+)", clean_text)
    title = title_match.group(1).strip() if title_match else "Exclusive Luxury Lifestyle Guide"
    
    # Image Prompt निकालना
    img_match = re.search(r"IMAGE_PROMPT:\s*(.+)", clean_text)
    img_prompt = img_match.group(1).strip() if img_match else "Luxury exotic product 8k realistic"
    
    # Content निकालना
    content_parts = clean_text.split("CONTENT:")
    body_content = content_parts[1].strip() if len(content_parts) > 1 else clean_text
    
    # Pollinations AI से फ्री ऑटोमैटिक HD फोटो URL बनाना
    encoded_prompt = urllib.parse.quote(f"{img_prompt}, 8k resolution, cinematic lighting, photorealistic, luxury aesthetic")
    hd_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=750&nologo=true"

    # Mobile-Friendly Responsive HTML डिज़ाइन तैयार करना
    final_html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.7; color: #222; max-width: 100%;">
        <!-- Featured HD Image (Mobile Optimized) -->
        <div style="text-align: center; margin-bottom: 25px;">
            <img src="{hd_image_url}" alt="{title}" style="width: 100%; max-width: 850px; height: auto; border-radius: 12px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); display: block; margin: 0 auto;" />
            <p style="font-size: 12px; color: #777; margin-top: 6px;">Exclusive High-Definition Visual Showcase</p>
        </div>

        <!-- Article Content -->
        <div style="font-size: 16px;">
            {body_content}
        </div>
    </div>
    """
    
    return title, final_html

def send_email_to_blogger(title, body_html):
    blogger_email = os.environ.get("BLOGGER_EMAIL")
    sender_email = os.environ.get("SENDER_EMAIL")
    sender_password = os.environ.get("SENDER_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = blogger_email
    msg['Subject'] = title
    msg.attach(MIMEText(body_html, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, blogger_email, msg.as_string())
        server.quit()
        print(f"Success: Post '{title}' published successfully with HD image!")
    except Exception as e:
        print(f"Error sending email to Blogger: {e}")

if __name__ == "__main__":
    raw_article = generate_luxury_article()
    title, full_html = parse_and_build_html(raw_article)
    send_email_to_blogger(title, full_html)
