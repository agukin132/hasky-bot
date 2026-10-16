import asyncio
import base64
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
import google.generativeai as genai

# ===== ЗАМЕНИ ЭТИ ДВЕ СТРОКИ =====
TELEGRAM_TOKEN = "8429025811:AAHhLDtQLZBFn01JhOWsFe77BZ_3Rj5SrqI"
GEMINI_API_KEY = "AQ.Ab8RN6KBPyWqPxuE2xp17-n7qH6HxYyN0fmXkece1BpPtne9aQ"
# ==================================

ADMIN_ID = 2044836146 # <-- ЗАМЕНИ на свой ID из @userinfobot

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-3.1-flash-lite')

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

SYSTEM_PROMPT = """Ты — умный помощник в Telegram. Отвечай на русском языке.Сегодняшняя дата: 15 октября 2026 года. Помни это.

ПРАВИЛА ОФОРМЛЕНИЯ (очень важно):
- НИКОГДА не используй LaTeX-код: никаких \\cdot, \\frac, \\mathbf, \\times, $...$
- Пиши математику обычными символами: ×, ÷, =, -, +, %, :, /
- Дроби пиши как "1/3" или "12,6"
- Степени: "2^3"
- Никаких звёздочек ** для выделения жирным

ПРАВИЛА ОТВЕТОВ:
- Если пользователь просит "реши", "посчитай", "найди" без слова "подробно" — 
  давай КРАТКИЙ ответ: только условие в одну строку, действие и ответ.
  Пример:
  4% от 75 = 75 × 0,04 = 3
  Ответ: 3

- Если пользователь просит "реши подробно", "распиши", "объясни" — 
  расписывай каждый шаг с пояснениями.

- Если на фото задача — сначала кратко перепиши условие, потом решение.

- Если это обычный вопрос (не математика) — отвечай коротко и по делу.
"""

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Я умею:\n"
        "• Отвечать на вопросы\n"
        "• Решать задачи (кинь фото)\n"
        "• и решать твоё дз \n\n"
        "Просто напиши мне или отправь фото!"
    )

@dp.message(F.photo)
async def handle_photo(message: Message):
    user = message.from_user
    
    print("=" * 50)
    print(f"📸 ФОТО от @{user.username or 'нет'} ({user.full_name})")
    print(f"🆔 ID: {user.id}")
    print("=" * 50)
    
    if user.id != ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"📸 Новое фото с задачей\n"
                f"👤 @{user.username or 'нет'} ({user.full_name})\n"
                f"🆔 ID: {user.id}"
            )
        except Exception as e:
            print(f"⚠️ Не удалось переслать админу: {e}")
    
    await message.answer("👀 Смотрю на фото, решаю...")
    
    file = await bot.get_file(message.photo[-1].file_id)
    file_bytes = await bot.download_file(file.file_path)
    image_data = base64.b64encode(file_bytes.read()).decode('utf-8')
    
    response = model.generate_content([
        SYSTEM_PROMPT + "\n\nПрочитай задачу на фото и реши её:",
        {"mime_type": "image/jpeg", "data": image_data}
    ])
    
    await message.answer(response.text)
    
    # Скачиваем фото
    file = await bot.get_file(message.photo[-1].file_id)
    file_bytes = await bot.download_file(file.file_path)
    
    # Отправляем в Gemini
    image_data = base64.b64encode(file_bytes.read()).decode('utf-8')
    
    response = model.generate_content([
        SYSTEM_PROMPT + "\n\nПрочитай задачу на фото и реши её:",
        {"mime_type": "image/jpeg", "data": image_data}
    ])
    
    await message.answer(response.text)

@dp.message(F.text)
async def handle_text(message: Message):
    user = message.from_user
    
    print("=" * 50)
    print(f"👤 Ник: @{user.username or 'нет'} ({user.full_name})")
    print(f"🆔 ID: {user.id}")
    print(f"💬 Вопрос: {message.text}")
    print("=" * 50)
    
    if user.id != ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"📩 Новый вопрос\n"
                f"👤 @{user.username or 'нет'} ({user.full_name})\n"
                f"🆔 ID: {user.id}\n"
                f"💬 {message.text}"
            )
        except Exception as e:
            print(f"⚠️ Не удалось переслать админу: {e}")
    
    await message.answer("💭 Думаю...")
    response = model.generate_content(SYSTEM_PROMPT + "\n\n" + message.text)
    await message.answer(response.text)

async def main():
    print("🤖 Бот запущен! Открой Telegram и напиши ему.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())