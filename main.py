import telebot
import json
import os
import uuid
from threading import Thread
from flask import Flask, request

# ================= НАСТРОЙКИ =================
TOKEN = '8509662585:AAErQX0z1mvVj20npoqfFtuKRnzShBlUq0U'  # Вставь токен от BotFather
ADMIN_ID = 6049379160     # Вставь твой цифровой ID (числом, без кавычек)
# =============================================

bot = telebot.TeleBot(TOKEN)
DB_FILE = 'database.json'

# --- ЧАСТЬ 1: ВЕЧНАЯ ЖИЗНЬ (Flask Сервер) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Бот работает."

def run_http():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_http)
    t.start()

# --- ЧАСТЬ 2: БАЗА ДАННЫХ (Файлы) ---
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

# --- ЧАСТЬ 3: ЛОГИКА БОТА ---

# Обработка ссылок (для всех) и команды старт
@bot.message_handler(commands=['start'])
def start_handler(message):
    args = message.text.split()
    
    # Если перешли по ссылке с кодом
    if len(args) > 1:
        code = args[1]
        db = load_db()
        
        if code in db:
            file_data = db[code]
            f_id = file_data['id']
            f_type = file_data['type']
            
            try:
                msg = "Вот твой файл 👇"
                if f_type == 'photo': bot.send_photo(message.chat.id, f_id, caption=msg)
                elif f_type == 'video': bot.send_video(message.chat.id, f_id, caption=msg)
                elif f_type == 'audio': bot.send_audio(message.chat.id, f_id, caption=msg)
                elif f_type == 'voice': bot.send_voice(message.chat.id, f_id, caption=msg)
                else: bot.send_document(message.chat.id, f_id, caption=msg)
            except:
                bot.send_message(message.chat.id, "❌ Ошибка: Файл был удален из Telegram.")
        else:
            bot.send_message(message.chat.id, "⛔ Ссылка недействительна.")
    
    # Если просто нажали старт
    else:
        if message.from_user.id == ADMIN_ID:
            bot.send_message(message.chat.id, "👨‍💻 Привет, Создатель!\nКидай мне файлы, я сделаю из них ссылки.")
        else:
            bot.send_message(message.chat.id, "👋 Я файловое хранилище. Я ничего не делаю просто так, нужна ссылка.")

# Добавление файлов (Только админ)
@bot.message_handler(content_types=['document', 'photo', 'video', 'audio', 'voice'])
def handle_files(message):
    if message.from_user.id != ADMIN_ID:
        return # Игнорируем чужаков

    f_id = None
    f_type = 'doc'

    if message.content_type == 'document':
        f_id = message.document.file_id
        f_type = 'doc'
    elif message.content_type == 'photo':
        f_id = message.photo[-1].file_id
        f_type = 'photo'
    elif message.content_type == 'video':
        f_id = message.video.file_id
        f_type = 'video'
    elif message.content_type == 'audio':
        f_id = message.audio.file_id
        f_type = 'audio'
    elif message.content_type == 'voice':
        f_id = message.voice.file_id
        f_type = 'voice'

    if f_id:
        unique_code = str(uuid.uuid4())[:8] # Генерируем код
        db = load_db()
        db[unique_code] = {'id': f_id, 'type': f_type}
        save_db(db)
        
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={unique_code}"
        
        bot.reply_to(message, f"✅ **Файл сохранен!**\n\n🔗 Ссылка для друга:\n`{link}`", parse_mode='Markdown')

# Запуск
keep_alive() # Запускаем веб-сервер
bot.infinity_polling() # Запускаем бота
