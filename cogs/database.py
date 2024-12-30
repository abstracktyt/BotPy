import sqlite3
import aiosqlite
import json
from typing import Optional, Dict, Any

class Database:
    def __init__(self):
        self.db_path = 'bot.db'
        self._init_db()

    def _init_db(self):
        """Инициализация базы данных"""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Таблица настроек серверов
            c.execute('''CREATE TABLE IF NOT EXISTS guild_settings
                        (guild_id INTEGER PRIMARY KEY,
                         settings TEXT)''')
            
            # Таблица статистики
            c.execute('''CREATE TABLE IF NOT EXISTS statistics
                        (guild_id INTEGER,
                         timestamp TEXT,
                         member_count INTEGER,
                         online_count INTEGER,
                         channel_count INTEGER,
                         PRIMARY KEY (guild_id, timestamp))''')
            
            # Таблица тикетов
            c.execute('''CREATE TABLE IF NOT EXISTS tickets
                        (ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                         guild_id INTEGER,
                         channel_id INTEGER,
                         user_id INTEGER,
                         created_at TEXT,
                         closed_at TEXT,
                         reason TEXT)''')
            
            # Таблица модерации
            c.execute('''CREATE TABLE IF NOT EXISTS moderation_actions
                        (action_id INTEGER PRIMARY KEY AUTOINCREMENT,
                         guild_id INTEGER,
                         moderator_id INTEGER,
                         user_id INTEGER,
                         action_type TEXT,
                         reason TEXT,
                         timestamp TEXT)''')
            
            # Таблица приветствий
            c.execute('''CREATE TABLE IF NOT EXISTS welcome_messages
                        (guild_id INTEGER PRIMARY KEY,
                         channel_id INTEGER,
                         message TEXT,
                         autorole_id INTEGER)''')
            
            conn.commit()

    async def get_guild_settings(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Получить настройки сервера"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT settings FROM guild_settings WHERE guild_id = ?',
                (guild_id,)
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    return json.loads(result[0])
                return None

    async def update_guild_setting(self, guild_id: int, key: str, value: Any):
        """Обновить настройку сервера"""
        settings = await self.get_guild_settings(guild_id) or {}
        settings[key] = value
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT OR REPLACE INTO guild_settings (guild_id, settings)
                   VALUES (?, ?)''',
                (guild_id, json.dumps(settings))
            )
            await db.commit()

    async def log_moderation(self, guild_id: int, moderator_id: int, user_id: int,
                           action_type: str, reason: str = None):
        """Логирование действий модерации"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO moderation_actions 
                   (guild_id, moderator_id, user_id, action_type, reason, timestamp)
                   VALUES (?, ?, ?, ?, ?, datetime('now'))''',
                (guild_id, moderator_id, user_id, action_type, reason)
            )
            await db.commit()

    async def create_ticket(self, guild_id: int, channel_id: int, user_id: int, reason: str = None):
        """Создание тикета"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO tickets 
                   (guild_id, channel_id, user_id, created_at, reason)
                   VALUES (?, ?, ?, datetime('now'), ?)''',
                (guild_id, channel_id, user_id, reason)
            )
            await db.commit()

    async def close_ticket(self, channel_id: int):
        """Закрытие тикета"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''UPDATE tickets 
                   SET closed_at = datetime('now')
                   WHERE channel_id = ? AND closed_at IS NULL''',
                (channel_id,)
            )
            await db.commit()

    async def update_statistics(self, guild_id: int, member_count: int,
                              online_count: int, channel_count: int):
        """Обновление статистики"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO statistics 
                   (guild_id, timestamp, member_count, online_count, channel_count)
                   VALUES (?, datetime('now'), ?, ?, ?)''',
                (guild_id, member_count, online_count, channel_count)
            )
            await db.commit()

    async def get_welcome_settings(self, guild_id: int):
        """Получить настройки приветствий"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                '''SELECT channel_id, message, autorole_id 
                   FROM welcome_messages 
                   WHERE guild_id = ?''',
                (guild_id,)
            ) as cursor:
                return await cursor.fetchone()

    async def set_welcome_settings(self, guild_id: int, channel_id: int,
                                 message: str = None, autorole_id: int = None):
        """Установить настройки приветствий"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT OR REPLACE INTO welcome_messages 
                   (guild_id, channel_id, message, autorole_id)
                   VALUES (?, ?, ?, ?)''',
                (guild_id, channel_id, message, autorole_id)
            )
            await db.commit() 