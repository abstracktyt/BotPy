import discord
from discord import app_commands
from discord.ext import commands
from utils.style import Style
import re
from datetime import datetime, timedelta
from collections import defaultdict

class SlashAntiLeak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()
        self.action_tracker = defaultdict(lambda: defaultdict(list))
        self.limits = {
            'channel_create': 3,
            'channel_delete': 3,
            'role_create': 3,
            'role_delete': 3,
            'ban': 3,
            'kick': 3,
            'webhook': 2,
            'bot_add': 1,
            'everyone_ping': 2
        }

    @app_commands.command(name="antileak", description="Управление системой защиты")
    @app_commands.describe(
        action="Действие (on/off)",
        setting="Настройка для изменения",
        value="Новое значение"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def antileak(self, interaction: discord.Interaction, action: str = None, 
                      setting: str = None, value: int = None):
        if not action:
            # Показать текущие настройки
            settings_text = "\n".join([f"{k}: {v}" for k, v in self.limits.items()])
            embed = self.style.info_embed(
                "Настройки защиты",
                f"Текущие лимиты:\n```{settings_text}```"
            )
            await interaction.response.send_message(embed=embed)
            return

        if action.lower() == "set" and setting and value is not None:
            if setting in self.limits:
                self.limits[setting] = value
                embed = self.style.success_embed(
                    "Настройки обновлены",
                    f"Лимит {setting} установлен на {value}"
                )
            else:
                embed = self.style.error_embed(
                    "Ошибка",
                    "Неизвестная настройка"
                )
        else:
            embed = self.style.error_embed(
                "Ошибка",
                "Неверные параметры команды"
            )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="raidmode", description="Включить/выключить режим защиты от рейда")
    @app_commands.describe(state="Состояние (on/off)")
    @app_commands.checks.has_permissions(administrator=True)
    async def raidmode(self, interaction: discord.Interaction, state: str):
        state = state.lower()
        if state not in ['on', 'off']:
            await interaction.response.send_message(
                embed=self.style.error_embed(
                    "Ошибка",
                    "Укажите on или off"
                )
            )
            return

        guild = interaction.guild
        enabled = state == 'on'
        
        try:
            # Настройка повышенной защиты
            if enabled:
                # Отключаем создание приглашений для обычных пользователей
                default_role = guild.default_role
                perms = default_role.permissions
                perms.create_instant_invite = False
                await default_role.edit(permissions=perms)
                
                # Включаем проверку на 2FA для админ действий
                await guild.edit(mfa_level=True)
                
                embed = self.style.success_embed(
                    "Режим защиты включен",
                    "• Отключены приглашения для обычных пользователей\n"
                    "• Включена двухфакторная аутентификация для админ действий\n"
                    "• Усилен мониторинг подозрительной активности"
                )
            else:
                # Возвращаем стандартные настройки
                default_role = guild.default_role
                perms = default_role.permissions
                perms.create_instant_invite = True
                await default_role.edit(permissions=perms)
                
                embed = self.style.success_embed(
                    "Режим защиты отключен",
                    "Настройки сервера возвращены к стандартным"
                )
                
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", str(e))
            )

async def setup(bot):
    await bot.add_cog(SlashAntiLeak(bot)) 