import threading
import logging
from web.app import app, socketio, bot
import config

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_flask():
    """Запуск Flask сервера"""
    try:
        logger.info("Запуск веб-сервера на http://localhost:5000")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, log_output=True)
    except Exception as e:
        logger.error(f"Ошибка запуска веб-сервера: {e}")
        raise

def run_bot():
    """Запуск Discord бота"""
    try:
        logger.info("Запуск Discord бота")
        bot.run(config.TOKEN)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")
        raise

if __name__ == '__main__':
    try:
        # Запускаем бота в отдельном потоке
        logger.info("Инициализация приложения...")
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.start()
        
        # Запускаем веб-сервер
        run_flask()
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise 