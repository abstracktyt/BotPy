import discord
from discord import app_commands
from discord.ext import commands
from utils.style import Style
import asyncio

class SlashTickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()

    @app_commands.command(name="ticket", description="Создать тикет для обращения к администрации")
    @app_commands.describe(reason="Причина создания тикета")
    async def ticket(self, interaction: discord.Interaction, reason: str = None):
        try:
            # Проверяем существование категории
            category = discord.utils.get(interaction.guild.categories, name="Тикеты")
            if not category:
                category = await interaction.guild.create_category(
                    name="Тикеты",
                    overwrites={
                        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
                    }
                )

            # Создаем канал тикета
            channel = await interaction.guild.create_text_channel(
                f'ticket-{interaction.user.name}',
                category=category,
                overwrites={
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
                }
            )

            embed = self.style.info_embed(
                "Тикет создан",
                f"Ваш тикет: {channel.mention}\n"
                f"Для закрытия используйте `/close`"
            )
            if reason:
                embed.add_field(name="Причина", value=reason)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Отправляем приветственное сообщение в канал тикета
            welcome_embed = self.style.info_embed(
                "Новый тикет",
                f"Тикет создан пользователем {interaction.user.mention}\n"
                f"Причина: {reason or 'Не указана'}\n\n"
                "Опишите вашу проблему или вопрос. Администрация ответит вам в ближайшее время."
            )
            await channel.send(embed=welcome_embed)

        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", str(e)),
                ephemeral=True
            )

    @app_commands.command(name="close", description="Закрыть текущий тикет")
    async def close(self, interaction: discord.Interaction):
        if not interaction.channel.name.startswith('ticket-'):
            await interaction.response.send_message(
                embed=self.style.error_embed(
                    "Ошибка",
                    "Эта команда работает только в каналах тикетов!"
                ),
                ephemeral=True
            )
            return

        embed = self.style.warning_embed(
            "Закрытие тикета",
            "Тикет будет закрыт через 5 секунд..."
        )
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @app_commands.command(name="add", description="Добавить пользователя в тикет")
    @app_commands.describe(user="Пользователь для добавления в тикет")
    async def add_to_ticket(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith('ticket-'):
            await interaction.response.send_message(
                embed=self.style.error_embed(
                    "Ошибка",
                    "Эта команда работает только в каналах тикетов!"
                ),
                ephemeral=True
            )
            return

        try:
            await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
            embed = self.style.success_embed(
                "Пользователь добавлен",
                f"{user.mention} был добавлен в тикет"
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", str(e)),
                ephemeral=True
            )

    @app_commands.command(name="remove", description="Удалить пользователя из тикета")
    @app_commands.describe(user="Пользователь для удаления из тикета")
    async def remove_from_ticket(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.channel.name.startswith('ticket-'):
            await interaction.response.send_message(
                embed=self.style.error_embed(
                    "Ошибка",
                    "Эта команда работает только в каналах тикетов!"
                ),
                ephemeral=True
            )
            return

        try:
            await interaction.channel.set_permissions(user, overwrite=None)
            embed = self.style.success_embed(
                "Пользователь удален",
                f"{user.mention} был удален из тикета"
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", str(e)),
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(SlashTickets(bot)) 