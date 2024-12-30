import discord
from discord import app_commands, ui
from discord.ext import commands
from utils.style import Style
import asyncio
import random
from typing import Optional
import datetime

class ManualView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✨ Интерактивный режим", style=discord.ButtonStyle.blurple, custom_id="interactive_mode", emoji="🎮")
    async def interactive_mode(self, interaction: discord.Interaction, button: discord.ui.Button):
        style = Style()
        
        # Улучшенное меню категорий с анимированными эмодзи
        category_select = ui.Select(
            placeholder="💫 Выберите категорию для изучения",
            options=[
                discord.SelectOption(
                    label="Модерация", 
                    emoji="<a:mod_shield:123456789>", # Анимированный щит
                    value="mod",
                    description="⚔️ Управление сервером и участниками"
                ),
                discord.SelectOption(
                    label="Тикеты",
                    emoji="<a:sparkle_ticket:123456790>", # Анимированный тикет
                    value="tickets", 
                    description="📨 Система обращений и поддержки"
                ),
                discord.SelectOption(
                    label="Статистика",
                    emoji="<a:chart_growing:123456791>", # Анимированный график
                    value="stats",
                    description="📊 Аналитика и детальные отчеты"
                ),
                discord.SelectOption(
                    label="Защита",
                    emoji="<a:security_lock:123456792>", # Анимированный замок
                    value="protection",
                    description="🛡️ Комплексная защита сервера"
                ),
                discord.SelectOption(
                    label="Утилиты",
                    emoji="<a:tools_spinning:123456793>", # Крутящиеся инструменты
                    value="utils",
                    description="🔧 Полезные инструменты"
                ),
                discord.SelectOption(
                    label="Развлечения",
                    emoji="<a:party_blob:123456794>", # Танцующий блоб
                    value="fun",
                    description="🎉 Игры и веселье"
                )
            ]
        )
        
        async def category_callback(interaction: discord.Interaction):
            category = category_select.values[0]
            category_embeds = {
                "mod": style.mod_embed(
                    "🛡️ Система модерации",
                    "```ansi\n\u001b[1;31mМодерация и управление\u001b[0m```\n"
                    "**Основные команды:**\n"
                    "⚔️ `/ban` - Блокировка пользователя\n"
                    "🔇 `/mute` - Отключение чата\n" 
                    "⚠️ `/warn` - Выдача предупреждения\n"
                    "🧹 `/clear` - Очистка сообщений"
                ),
                "tickets": style.info_embed(
                    "🎫 Система тикетов",
                    "```ansi\n\u001b[1;33mПоддержка пользователей\u001b[0m```\n"
                    "**Основные команды:**\n"
                    "📩 `/ticket` - Создать обращение\n"
                    "🔒 `/close` - Закрыть тикет\n"
                    "➕ `/add` - Добавить участника"
                ),
                "stats": style.stats_embed(
                    "📊 Статистика",
                    "```ansi\n\u001b[1;34mАналитика сервера\u001b[0m```\n"
                    "**Основные команды:**\n"
                    "📈 `/stats` - Общая статистика\n"
                    "👑 `/top` - Топ участников\n"
                    "📊 `/activity` - Активность"
                ),
                "protection": style.info_embed(
                    "🛡️ Защита",
                    "```ansi\n\u001b[1;35mБезопасность сервера\u001b[0m```\n"
                    "**Основные функции:**\n"
                    "🚫 • Продвинутый антиспам\n"
                    "⚔️ • Защита от рейдов\n"
                    "🔍 • Умный фильтр контента"
                ),
                "utils": style.info_embed(
                    "🛠️ Утилиты",
                    "```ansi\n\u001b[1;36mПолезные инструменты\u001b[0m```\n"
                    "**Основные команды:**\n"
                    "📊 `/poll` - Создать голосование\n"
                    "🎲 `/random` - Случайное число\n"
                    "⏰ `/remind` - Напоминание"
                ),
                "fun": style.info_embed(
                    "🎮 Развлечения", 
                    "```ansi\n\u001b[1;32mИгры и веселье\u001b[0m```\n"
                    "**Основные команды:**\n"
                    "🎲 `/game` - Мини-игры\n"
                    "😂 `/meme` - Случайный мем\n"
                    "🔮 `/8ball` - Шар предсказаний"
                )
            }
            
            embed = category_embeds.get(
                category,
                style.info_embed("Категория", "Информация скоро появится")
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/123456789.gif")
            embed.set_footer(text=f"Запрошено {interaction.user}", icon_url=interaction.user.avatar.url)
            embed.timestamp = datetime.datetime.now()
            
            await interaction.response.edit_message(embed=embed)

        category_select.callback = category_callback
        view = ui.View(timeout=None)
        view.add_item(category_select)
        
        main_embed = style.info_embed(
            "✨ Интерактивный режим",
            "```ansi\n"
            "\u001b[1;35mДобро пожаловать в улучшенный интерактивный режим!\u001b[0m\n"
            "```\n"
            "**🎯 Выберите категорию для подробного изучения:**\n\n"
            "```ml\n'Используйте красочное меню ниже для навигации'```"
        )
        main_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/123456790.gif")
        main_embed.set_footer(text="💫 Нажмите на категорию для получения подробной информации")
        main_embed.timestamp = datetime.datetime.now()
        
        await interaction.response.edit_message(
            embed=main_embed,
            view=view
        )

    @discord.ui.button(label="🎨 Темы оформления", style=discord.ButtonStyle.green, custom_id="themes", emoji="✨")
    async def themes(self, interaction: discord.Interaction, button: discord.ui.Button):
        class ThemeModal(ui.Modal, title="✨ Настройка оформления"):
            theme = ui.TextInput(
                label="🎨 Тема оформления",
                placeholder="dark/light/custom/rainbow",
                min_length=4,
                max_length=7
            )
            accent_color = ui.TextInput(
                label="🌈 Акцентный цвет (HEX)",
                placeholder="#ff5555",
                required=False,
                min_length=7,
                max_length=7
            )
            
            async def on_submit(self, interaction: discord.Interaction):
                style = Style()
                embed = style.success_embed(
                    "✨ Настройки успешно применены",
                    f"```ansi\n"
                    f"\u001b[1;32m• Тема:\u001b[0m **{self.theme.value}**\n"
                    f"\u001b[1;33m• Цвет:\u001b[0m **{self.accent_color.value or '🌈 Радужный'}**\n"
                    f"```"
                )
                embed.set_footer(text="Настройки сохранены", icon_url=interaction.user.avatar.url)
                embed.timestamp = datetime.datetime.now()
                await interaction.response.send_message(embed=embed, ephemeral=True)

        await interaction.response.send_modal(ThemeModal())

class HelpManual(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()
        self.MANUAL_CHANNEL_ID = 1322964852058230955

    @app_commands.command(name="manual", description="📚 Отправить интерактивную инструкцию в канал")
    @app_commands.checks.has_permissions(administrator=True)
    async def send_manual(self, interaction: discord.Interaction):
        channel = self.bot.get_channel(self.MANUAL_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message(
                embed=self.style.error_embed(
                    "❌ Ошибка",
                    "Канал инструкции не найден!"
                ),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=self.style.success_embed(
                "✅ Успешно",
                "Интерактивное руководство создано!"
            ),
            ephemeral=True
        )
        
        await channel.purge()
        
        menu_embed = self.style.info_embed(
            "🌟 Интерактивное руководство",
            "```ansi\n"
            "\u001b[1;35m✨ Добро пожаловать в улучшенное руководство!\u001b[0m\n"
            "```\n"
            "**Нажмите на кнопки ниже и исследуйте возможности бота:**\n"
            "```ml\n"
            "🎮 'Интерактивный режим' - Подробное описание команд\n"
            "🎨 'Темы оформления'     - Настройка внешнего вида\n"
            "```"
        )
        menu_embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/123456791.gif")
        menu_embed.set_footer(text="Создано с ❤️")
        menu_embed.timestamp = datetime.datetime.now()
        await channel.send(embed=menu_embed, view=ManualView())

async def setup(bot):
    await bot.add_cog(HelpManual(bot))