import discord
from discord.ext import commands
from utils.style import Style
import datetime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        🔨 Выгнать участника с сервера
        
        Использование:
        !kick @пользователь [причина]
        """
        try:
            await member.kick(reason=reason)
            embed = self.style.success_embed(
                "Участник выгнан",
                f"{self.style.EMOJIS['kick']} {member.mention} был выгнан с сервера"
            )
            embed.add_field(name="Модератор", value=ctx.author.mention)
            if reason:
                embed.add_field(name="Причина", value=reason)
            await ctx.send(embed=embed)
            
            # Отправка лога
            log_embed = self.style.mod_log_embed("Кик", ctx.author, member, reason)
            log_channel = discord.utils.get(ctx.guild.channels, name="mod-logs")
            if log_channel:
                await log_channel.send(embed=log_embed)
                
        except Exception as e:
            await ctx.send(embed=self.style.error_embed("Ошибка", str(e)))

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        ⚔️ Забанить участника на сервере
        
        Использование:
        !ban @пользователь [причина]
        """
        try:
            await member.ban(reason=reason)
            embed = self.style.success_embed(
                "Участник забанен",
                f"{self.style.EMOJIS['ban']} {member.mention} был забанен на сервере"
            )
            embed.add_field(name="Модератор", value=ctx.author.mention)
            if reason:
                embed.add_field(name="Причина", value=reason)
            await ctx.send(embed=embed)
            
            # Отправка лога
            log_embed = self.style.mod_log_embed("Бан", ctx.author, member, reason)
            log_channel = discord.utils.get(ctx.guild.channels, name="mod-logs")
            if log_channel:
                await log_channel.send(embed=log_embed)
                
        except Exception as e:
            await ctx.send(embed=self.style.error_embed("Ошибка", str(e)))

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """
        🧹 Очистить сообщения в канале
        
        Использование:
        !clear <количество>
        """
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            embed = self.style.success_embed(
                "Сообщения удалены",
                f"{self.style.EMOJIS['success']} Удалено {len(deleted)-1} сообщений"
            )
            msg = await ctx.send(embed=embed)
            await msg.delete(delay=5)
        except Exception as e:
            await ctx.send(embed=self.style.error_embed("Ошибка", str(e)))

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int, *, reason=None):
        """
        🔇 Замутить участника
        
        Использование:
        !mute @пользователь <время_в_минутах> [причина]
        """
        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not muted_role:
                muted_role = await ctx.guild.create_role(name="Muted")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, speak=False, send_messages=False)

            await member.add_roles(muted_role)
            embed = self.style.success_embed(
                "Участник замучен",
                f"{self.style.EMOJIS['mute']} {member.mention} получил мут на {duration} минут"
            )
            embed.add_field(name="Модератор", value=ctx.author.mention)
            if reason:
                embed.add_field(name="Причина", value=reason)
            await ctx.send(embed=embed)

            # Отправка лога
            log_embed = self.style.mod_log_embed("Мут", ctx.author, member, f"{duration} минут | {reason if reason else 'Причина не указана'}")
            log_channel = discord.utils.get(ctx.guild.channels, name="mod-logs")
            if log_channel:
                await log_channel.send(embed=log_embed)

        except Exception as e:
            await ctx.send(embed=self.style.error_embed("Ошибка", str(e)))

async def setup(bot):
    await bot.add_cog(Moderation(bot)) 