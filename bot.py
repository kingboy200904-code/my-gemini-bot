import telebot
from groq import Groq
import base64
import os
import time
from flask import Flask
from threading import Thread

# Serverni o'chib qolmasligi uchun kichik Web-interfeys
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run(): app.run(host='0.0.0.0', port=8080)

# MA'LUMOTLAR (TOKENingizni va Kalitingizni tekshirib qo'ying)
TOKEN = "8446115576:AAH49k8t0IKDtMFoghHNq83K3gF0nejqzOc"
GROQ_API_KEY = "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"

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
        
        base_64_image = encode_image("img.jpg")
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[{"role": "user", "content": [{"type": "text", "text": "Rasmda nima bor? O'zbekcha javob ber."}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base_64_image}"}}]}]
        )
        bot.reply_to(message, response.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Rasm xatosi: {e}")

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    try:
        res = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[{"role": "user", "content": message.text}]
        )
        bot.reply_to(message, res.choices[0].message.content)
    except Exception as e:
        bot.reply_to(message, f"Xato: {e}")

if __name__ == "__main__":
    t = Thread(target=run)
    t.daemon = True # Shu qatorni qo'shing
    t.start()
    bot.remove_webhook() # Shu qatorni qo'shing
    bot.infinity_polling(skip_pending=True) # skip_pending=True qo'shing
