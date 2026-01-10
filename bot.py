import telebot
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# 1. SERVERNI TIRIQLAYDI
app = Flask('')
@app.route('/')
def home(): return "Gemini Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)

# 2. KALITLAR (O'zingiznikini qo'ying)
TELEGRAM_TOKEN = "8446115576:AAH49k8t0IKDtMFoghHNq83K3gF0nejqzOc"
GEMINI_API_KEY = "AIzaSyADPWBzISmbtMR5vMeAui08BQ8GBL3uiSY"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# RASM UCHUN
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("image.jpg", "wb") as f:
            f.write(downloaded_file)
        
        img = genai.upload_file("image.jpg")
        response = model.generate_content(["Rasmdagi matnlarni o'qi va o'zbekchaga tarjima qil. Matn bo'lmasa rasmda nima borligini ayt.", img])
        
        bot.reply_to(message, response.text)
        os.remove("image.jpg")
    except Exception as e:
        bot.reply_to(message, f"Xato yuz berdi: {e}")

# MATN UCHUN
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Xato: {e}")

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.infinity_polling()
