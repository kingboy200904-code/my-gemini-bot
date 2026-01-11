import telebot
from groq import Groq
import base64
import os
from flask import Flask
from threading import Thread

# 1. SERVERNI TIRIQLASH
app = Flask('')
@app.route('/')
def home(): return "Groq Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)

# 2. MA'LUMOTLAR (TOKEN va KEY'ni aniq qo'ying)
TOKEN = "8446115576:AAHqk8tOIKDtWFoghHNq83K3gF0nejqzOc"
GROQ_API_KEY = "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" # <--- Kalitni to'liq qo'ying!

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TOKEN)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("img.jpg", 'wb') as f: f.write(downloaded_file)
        
        base64_image = encode_image("img.jpg")
        
        # MODEL NOMI: llama-3.2-90b-vision-preview
        response = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": "Rasmdagi matnni o'qi va o'zbekchaga tarjima qil. Matn bo'lmasa rasmda nima borligini ayt."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}]
        )
        bot.reply_to(message, response.choices[0].message.content)
        os.remove("img.jpg")
    except Exception as e:
        bot.reply_to(message, f"Xato: {e}")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": message.text}]
        )
        bot.reply_to(message, completion.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Xato: {e}")

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
