import telebot
from flask import Flask
from threading import Thread
import time

# ================= НАСТРОЙКИ =================
TOKEN = '8509662585:AAErQX0z1mvVj20npoqfFtuKRnzShBlUq0U'
ADMIN_ID = 6049379160       # Ваш цифровой ID
CHANNEL_ID = --1003603094158  # ID Канала-склада (обязательно с -100)
# =============================================

bot = telebot.TeleBot(TOKEN)

# --- 1. ВЕЧНАЯ ЖИЗНЬ (СЕРВЕР) ---
app = Flask('')

@app.route('/')
def home():
    return "I'm alive! Бот работает."

def run_http():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_http)
    t.start()

# --- 2. ЛОГИКА БОТА ---

# Обработка команды /start (выдача файлов)
@bot.message_handler(commands=['start'])
def start_handler(message):
    args = message.text.split()
    
    # Если ссылка с кодом (t.me/bot?start=123)
    if len(args) > 1:
        msg_id = args[1] # Код - это номер сообщения в канале
        
        try:
            # Копируем сообщение из канала пользователю
            bot.copy_message(chat_id=message.chat.id, from_chat_id=CHANNEL_ID, message_id=int(msg_id))
        except Exception as e:
            bot.send_message(message.chat.id, "❌ Файл не найден или был удален из канала.")
    
    # Если просто /start
    else:
        if message.from_user.id == ADMIN_ID:
            bot.send_message(message.chat.id, "👨‍💻 Админ-панель.\nОтправь мне файл, чтобы сохранить его в базу.")
        else:
            bot.send_message(message.chat.id, "👋 Привет! Я выдаю файлы по ссылкам.")

# Добавление файлов (Только для Админа)
@bot.message_handler(content_types=['document', 'photo', 'video', 'audio', 'voice'])
def handle_files(message):
    if message.from_user.id != ADMIN_ID:
        return # Чужих игнорируем

    try:
        # 1. Пересылаем файл в канал-склад
        forwarded_msg = bot.forward_message(CHANNEL_ID, message.chat.id, message.message_id)
        
        # 2. Получаем ID этого сообщения в канале
        file_code = forwarded_msg.message_id
        
        # 3. Генерируем ссылку
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={file_code}"
        
        bot.reply_to(message, f"✅ **Файл сохранен в облаке!**\n\nОн больше никогда не пропадет.\n🔗 Ссылка:\n`{link}`", parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"Ошибка! Проверь, добавил ли ты меня в Админы канала {CHANNEL_ID}?\nТекст ошибки: {e}")

# --- ЗАПУСК ---
if __name__ == '__main__':
    keep_alive() # Запускаем веб-сервер
    bot.infinity_polling(skip_pending=True)
