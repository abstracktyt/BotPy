import discord
from discord import app_commands
from discord.ext import commands
from utils.style import Style
import asyncio

class SlashModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()

    @app_commands.command(name="ban", description="Забанить пользователя")
    @app_commands.describe(
        member="Пользователь для бана",
        reason="Причина бана",
        delete_messages="Удалить сообщения за последние X дней (0-7)"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, 
                 reason: str = None, delete_messages: int = 0):
        if delete_messages > 7:
            delete_messages = 7
            
        try:
            await member.ban(reason=reason, delete_message_days=delete_messages)
            embed = self.style.success_embed(
                "Бан",
                f"{member.mention} был забанен\nПричина: {reason or 'Не указана'}"
            )
            await interaction.response.send_message(embed=embed)
            
            # Логирование
            log_channel = discord.utils.get(interaction.guild.channels, name="mod-logs")
            if log_channel:
                log_embed = self.style.info_embed(
                    "Модерация | Бан",
                    f"Модератор: {interaction.user.mention}\n"
                    f"Нарушитель: {member.mention}\n"
                    f"Причина: {reason or 'Не указана'}"
                )
                await log_channel.send(embed=log_embed)
                
        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", str(e))
            )

    @app_commands.command(name="kick", description="Выгнать пользователя")
    @app_commands.describe(
        member="Пользователь для кика",
        reason="Причина кика"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        try:
            await member.kick(reason=reason)
            embed = self.style.success_embed(
                "Кик",
                f"{member.mention} был выгнан\nПричина: {reason or 'Не указана'}"
            )
            await interaction.response.send_message(embed=embed)
            
            # Логирование
            log_channel = discord.utils.get(interaction.guild.channels, name="mod-logs")
            if log_channel:
                log_embed = self.style.info_embed(
                    "Модерация | Кик",
                    f"Модератор: {interaction.user.mention}\n"
                    f"Нарушитель: {member.mention}\n"
                    f"Причина: {reason or 'Не указана'}"
                )
                await log_channel.send(embed=log_embed)
                
        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", str(e))
            )

    @app_commands.command(name="clear", description="Очистить сообщения")
    @app_commands.describe(
        amount="Количество сообщений для удаления",
        user="Удалить сообщения только от конкретного пользователя (необязательно)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int, user: discord.Member = None):
        if amount > 100:
            amount = 100
            
        await interaction.response.defer()
        
        try:
            if user:
                messages = []
                async for message in interaction.channel.history(limit=100):
                    if message.author == user and len(messages) < amount:
                        messages.append(message)
                await interaction.channel.delete_messages(messages)
                deleted = len(messages)
            else:
                deleted = len(await interaction.channel.purge(limit=amount))
            
            embed = self.style.success_embed(
                "Очистка сообщений",
                f"Удалено {deleted} сообщений"
            )
            await interaction.followup.send(embed=embed, delete_after=5)
            
        except Exception as e:
            await interaction.followup.send(
                embed=self.style.error_embed("Ошибка", str(e))
            )

    @app_commands.command(name="mute", description="Замутить пользователя")
    @app_commands.describe(
        member="Пользователь для мута",
        duration="Длительность мута в минутах",
        reason="Причина мута"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, 
                  duration: int, reason: str = None):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        
        if not muted_role:
            # Создаем роль мута
            try:
                muted_role = await interaction.guild.create_role(name="Muted")
                for channel in interaction.guild.channels:
                    await channel.set_permissions(muted_role, speak=False, send_messages=False)
            except Exception as e:
                await interaction.response.send_message(
                    embed=self.style.error_embed("Ошибка", f"Не удалось создать роль мута: {e}")
                )
                return

        try:
            await member.add_roles(muted_role, reason=reason)
            embed = self.style.success_embed(
                "Мут",
                f"{member.mention} получил мут на {duration} минут\n"
                f"Причина: {reason or 'Не указана'}"
            )
            await interaction.response.send_message(embed=embed)
            
            # Автоматическое размучивание
            await asyncio.sleep(duration * 60)
            if muted_role in member.roles:
                await member.remove_roles(muted_role)
                await interaction.channel.send(
                    embed=self.style.info_embed(
                        "Размут",
                        f"{member.mention} был автоматически размучен"
                    )
                )
                
        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", str(e))
            )

    @app_commands.command(name="unmute", description="Размутить пользователя")
    @app_commands.describe(member="Пользователь для размута")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        
        if not muted_role:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", "Роль мута не найдена")
            )
            return
            
        if muted_role not in member.roles:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", "Пользователь не находится в муте")
            )
            return
            
        try:
            await member.remove_roles(muted_role)
            embed = self.style.success_embed(
                "Размут",
                f"{member.mention} был размучен"
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                embed=self.style.error_embed("Ошибка", str(e))
            )

async def setup(bot):
    await bot.add_cog(SlashModeration(bot)) 