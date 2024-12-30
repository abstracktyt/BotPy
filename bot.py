import discord
from discord import app_commands
from discord.ext import commands
import config
import logging
import sqlite3
import datetime
import tracemalloc
import traceback
import sys
from cogs.database import Database
from utils.style import Style

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logger.propagate = False
tracemalloc.start()

class MultiBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        self.db = Database()
        self.style = Style()

    async def setup_hook(self):
        # Загружаем слэш-команды
        initial_extensions = [
            'cogs.slash_commands',
            'cogs.slash_moderation',
            'cogs.slash_tickets',
            'cogs.slash_stats',
            'cogs.slash_welcome',
            'cogs.slash_antileak',
            'cogs.database_commands',
            'cogs.help_manual'
        ]
        
        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
                logger.info(f'Модуль {extension} успешно загружен')
            except Exception as e:
                logger.error(f'Не удалось загрузить модуль {extension}: {e}')
                logger.error(f'Traceback: {traceback.format_exc()}')

        # Синхронизируем слэш-команды
        await self.tree.sync()
        logger.info("Слэш-команды синхронизированы")
        
        logger.info(f'Бот {self.user} успешно запущен!')
        logger.info(f'ID бота: {self.user.id}')
        logger.info(f'Количество серверов: {len(self.guilds)}')

    @app_commands.command(name="sync", description="Синхронизировать слэш-команды")
    @app_commands.checks.has_permissions(administrator=True)
    async def sync(self, interaction: discord.Interaction):
        """Синхронизировать слэш-команды"""
        try:
            await self.tree.sync()
            await interaction.response.send_message(
                embed=self.style.success_embed(
                    "Синхронизация",
                    "Слэш-команды успешно синхронизированы!"
                )
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed(
                    "Ошибка",
                    f"Не удалось синхронизировать команды: {str(e)}"
                )
            )

    async def on_command_error(self, ctx, error):
        logger.error(f'Ошибка при выполнении команды {ctx.command}: {error}')
        await ctx.send(
            embed=self.style.error_embed("Ошибка", str(error))
        )

bot = MultiBot()

# Дополнительные события для логирования
@bot.event
async def on_guild_join(guild):
    logger.info(f'Бот добавлен на сервер: {guild.name} (ID: {guild.id})')

@bot.event
async def on_guild_remove(guild):
    logger.info(f'Бот удален с сервера: {guild.name} (ID: {guild.id})')

@bot.event
async def on_command(ctx):
    logger.info(f'Команда {ctx.command} использована пользователем {ctx.author} на сервере {ctx.guild}')

bot.run(config.TOKEN) 