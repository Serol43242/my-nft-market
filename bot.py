import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils import executor
from dotenv import load_dotenv

# Загружаем токен из .env файла (безопасно!)
load_dotenv()

# Настройки
TOKEN = os.getenv("BOT_TOKEN")  # Токен берем из .env файла
WEB_APP_URL = "https://serol43242.github.io/my-nft-market/"  # ЗДЕСЬ ТВОЯ ССЫЛКА НА GITHUB PAGES

# Настройка логирования (чтобы видеть ошибки)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=TOKEN, parse_mode="HTML")  # parse_mode=HTML позволяет форматировать текст
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# ========== КОМАНДЫ ==========

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start
    Показывает красивое приветствие и кнопку для открытия Web App
    """
    # Создаем красивую клавиатуру с кнопкой для Web App
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="🚀 Открыть NFT Маркет", 
                web_app=WebAppInfo(url=WEB_APP_URL)
            )],
            [KeyboardButton(text="ℹ️ О проекте"), KeyboardButton(text="📊 Мои NFT")]
        ],
        resize_keyboard=True,  # Автоматически подгоняем размер
        input_field_placeholder="Выбери действие..."  # Подсказка в поле ввода
    )
    
    # Красивое приветствие
    welcome_text = f"""
🎨 <b>Добро пожаловать в NFT Маркет!</b> 🎨

Привет, {message.from_user.first_name}! 👋

Здесь ты можешь:
• Покупать уникальные NFT
• Продавать свои работы
• Участвовать в аукционах

👇 <b>Нажми на кнопку ниже, чтобы открыть маркет!</b>
    """
    
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "ℹ️ О проекте")
async def about_project(message: types.Message):
    """Информация о проекте"""
    text = """
<b>О проекте NFT Маркет</b>

Это инновационная платформа для торговли NFT в Telegram.
Мы используем технологию WebApp для удобного взаимодействия.

<b>Преимущества:</b>
✅ Быстрая регистрация
✅ Безопасные сделки
✅ Низкие комиссии
✅ Поддержка 24/7

🌐 Наш сайт: скоро...
📱 Версия: 1.0.0
    """
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "📊 Мои NFT")
async def my_nfts(message: types.Message):
    """Показывает NFT пользователя"""
    # Здесь ты можешь добавить логику для показа NFT пользователя
    text = """
🖼 <b>Твои NFT:</b>

У тебя пока нет NFT.
Купи свой первый NFT в маркете! 🚀
    """
    await message.answer(text)

# ========== ОБРАБОТКА ДАННЫХ ИЗ WEB APP ==========

@dp.message_handler(content_types=['web_app_data'])
async def handle_web_app_data(message: types.Message):
    """
    Получает данные из мини-приложения
    В твоем случае - логин пользователя
    """
    try:
        # Получаем данные от Web App
        data = json.loads(message.web_app_data.data)
        logger.info(f"Получены данные: {data}")
        
        nickname = data.get('nickname')
        
        if nickname:
            # Сохраняем никнейм пользователя (здесь можно подключить базу данных)
            # Например, сохранить в словарь или файл
            user_id = message.from_user.id
            
            # Красивый ответ пользователю
            response_text = f"""
✅ <b>Регистрация успешно завершена!</b>

👤 <b>Твой никнейм:</b> {nickname}
🆔 <b>ID в системе:</b> NFT-{user_id % 10000:04d}

🎉 Добро пожаловать в мир NFT!
Теперь ты можешь покупать и продавать NFT.
            """
            
            # Добавляем клавиатуру после регистрации
            keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🛒 В магазин", web_app=WebAppInfo(url=WEB_APP_URL))],
                    [KeyboardButton(text="👤 Мой профиль"), KeyboardButton(text="💰 Баланс")]
                ],
                resize_keyboard=True
            )
            
            await message.answer(response_text, reply_markup=keyboard)
        else:
            await message.answer("❌ Ошибка: никнейм не может быть пустым")
            
    except json.JSONDecodeError:
        await message.answer("❌ Ошибка: неверный формат данных")
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {e}")
        await message.answer(f"❌ Произошла ошибка: {str(e)}")

@dp.message_handler(commands=['profile'])
async def show_profile(message: types.Message):
    """Показывает профиль пользователя"""
    user = message.from_user
    
    # Здесь ты можешь загрузить данные пользователя из базы
    profile_text = f"""
👤 <b>Твой профиль</b>

<b>Имя:</b> {user.full_name}
<b>Username:</b> @{user.username if user.username else 'не указан'}
<b>ID:</b> <code>{user.id}</code>

📊 <b>Статистика:</b>
• NFT: 0
• Баланс: 0 TON
• Сделок: 0
    """
    
    await message.answer(profile_text)

# ========== ЗАПУСК БОТА ==========

async def on_startup(dp):
    """Действия при запуске бота"""
    # Устанавливаем кнопку меню (появится слева от поля ввода)
    await bot.set_chat_menu_button(
        menu_button=types.MenuButtonWebApp(
            text="🌐 Открыть Маркет",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    )
    
    # Отправляем сообщение админу (тебе) о запуске
    await bot.send_message(
        chat_id=8528849875,  # ЗДЕСЬ ТВОЙ TELEGRAM ID (можно узнать у @userinfobot)
        text="✅ <b>Бот NFT Маркет запущен!</b>\nВсе системы работают в штатном режиме."
    )
    
    logger.info("✅ Бот успешно запущен!")

if __name__ == '__main__':
    # Проверяем наличие токена
    if not TOKEN:
        logger.error("❌ Токен не найден! Создай файл .env и добавь BOT_TOKEN=твой_токен")
        exit(1)
    
    logger.info("🚀 Запуск бота...")
    # Запускаем бота
    executor.start_polling(
        dp, 
        skip_updates=True,  # Пропускаем старые сообщения
        on_startup=on_startup
    )