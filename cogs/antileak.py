import discord
from discord.ext import commands, tasks
import re
import logging
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger('discord')

class AntiLeak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token_pattern = re.compile(r'[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}|mfa\.[\w-]{84}')
        self.invite_pattern = re.compile(r'discord(?:\.gg|\.com\/invite)\/[a-zA-Z0-9]+')
        
        # Отслеживание действий
        self.action_tracker = defaultdict(lambda: defaultdict(list))
        self.bot_action_tracker = defaultdict(lambda: defaultdict(int))
        
        # Лимиты действий (в течение 10 секунд)
        self.limits = {
            'channel_create': 3,      # Создание каналов
            'role_create': 3,         # Создание ролей
            'channel_delete': 3,      # Удаление каналов
            'role_delete': 3,         # Удаление ролей
            'member_ban': 5,          # Баны участников
            'member_kick': 5,         # Кики участников
            'everyone_mention': 3,    # @everyone упоминания
            'webhook_create': 2,      # Создание вебхуков
            'bot_add': 2             # Добавление ботов
        }
        
        # Запуск очистки трекера
        self.clear_tracker.start()

    def cog_unload(self):
        self.clear_tracker.cancel()

    @tasks.loop(minutes=5)
    async def clear_tracker(self):
        """Очистка старых записей в трекере"""
        current_time = datetime.now()
        for guild_id in list(self.action_tracker.keys()):
            for action_type in list(self.action_tracker[guild_id].keys()):
                self.action_tracker[guild_id][action_type] = [
                    timestamp for timestamp in self.action_tracker[guild_id][action_type]
                    if current_time - timestamp < timedelta(minutes=5)
                ]

    async def check_and_handle_raid(self, guild_id: int, action_type: str, user_id: int, is_bot: bool = False):
        """Проверка на рейд и принятие мер"""
        current_time = datetime.now()
        tracker = self.bot_action_tracker if is_bot else self.action_tracker
        
        # Добавляем действие в трекер
        tracker[guild_id][action_type].append(current_time)
        
        # Проверяем количество действий за последние 10 секунд
        recent_actions = [
            action for action in tracker[guild_id][action_type]
            if current_time - action < timedelta(seconds=10)
        ]
        
        if len(recent_actions) > self.limits[action_type]:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            # Логируем инцидент
            logger.warning(f'Обнаружена подозрительная активность на сервере {guild.name}: {action_type} от {"бота" if is_bot else "пользователя"} {user_id}')
            
            if is_bot:
                # Если это бот, блокируем его
                try:
                    member = guild.get_member(user_id)
                    if member:
                        await member.ban(reason="Антирейд: Подозрительная активность бота")
                        logger.info(f'Бот {member.name} был заблокирован на сервере {guild.name}')
                except Exception as e:
                    logger.error(f'Ошибка при блокировке бота: {e}')
            
            return True
        return False

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Отслеживание добавления ботов"""
        if member.bot:
            logger.info(f'Бот {member.name} (ID: {member.id}) добавлен на сервер {member.guild.name}')
            
            # Проверяем на подозрительную активность
            is_raid = await self.check_and_handle_raid(
                member.guild.id, 
                'bot_add',
                member.id,
                True
            )
            
            if is_raid:
                try:
                    await member.ban(reason="Антирейд: Подозрительное добавление бота")
                    logger.warning(f'Бот {member.name} был автоматически заблокирован на сервере {member.guild.name}')
                except Exception as e:
                    logger.error(f'Ошибка при автоматической блокировке бота: {e}')

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await self.check_and_handle_raid(channel.guild.id, 'channel_create', channel.guild.me.id)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await self.check_and_handle_raid(channel.guild.id, 'channel_delete', channel.guild.me.id)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        await self.check_and_handle_raid(role.guild.id, 'role_create', role.guild.me.id)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.check_and_handle_raid(role.guild.id, 'role_delete', role.guild.me.id)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await self.check_and_handle_raid(guild.id, 'member_ban', guild.me.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        # Проверяем, был ли это кик
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                await self.check_and_handle_raid(member.guild.id, 'member_kick', entry.user.id)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            # Проверка на массовые @everyone упоминания от ботов
            if message.mention_everyone:
                is_raid = await self.check_and_handle_raid(
                    message.guild.id,
                    'everyone_mention',
                    message.author.id,
                    True
                )
                if is_raid:
                    try:
                        await message.author.ban(reason="Антирейд: Массовые @everyone упоминания")
                        logger.warning(f'Бот {message.author.name} заблокирован за массовые @everyone упоминания')
                    except Exception as e:
                        logger.error(f'Ошибка при блокировке бота за @everyone: {e}')

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        await self.check_and_handle_raid(channel.guild.id, 'webhook_create', channel.guild.me.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setraid(self, ctx, action: str, limit: int):
        """Установка лимитов для антирейд системы"""
        if action in self.limits:
            self.limits[action] = limit
            await ctx.send(f"Лимит для {action} установлен на {limit}")
            logger.info(f'Изменен лимит {action} на {limit} для сервера {ctx.guild.name}')
        else:
            await ctx.send("Неизвестный тип действия")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def raidlimits(self, ctx):
        """Просмотр текущих лимитов"""
        limits_text = "\n".join([f"{k}: {v}" for k, v in self.limits.items()])
        await ctx.send(f"Текущие лимиты:\n```{limits_text}```")

async def setup(bot):
    await bot.add_cog(AntiLeak(bot)) 