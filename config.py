import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Discord Bot Token (обязательно должен быть в .env)
TOKEN = os.getenv('DISCORD_TOKEN', 'MTMyMTUzNjg2MDc5NDY1MDY2NA.GdB_yj.WR9Mj9PUnFT8-wB0L9m5U-_Ackwg0xP_gOdTDc')
if not TOKEN:
    raise ValueError("Не найден DISCORD_TOKEN в файле .env")

# Flask настройки
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# База данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')

# Настройки веб-интерфейса
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
WEB_PORT = int(os.getenv('WEB_PORT', 5000))

# Базовая директория проекта
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Настройки базы данных SQLite
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False