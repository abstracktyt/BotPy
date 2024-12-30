import discord
from discord.ext import commands
import asyncio
from utils.style import Style

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()

    @commands.command()
    async def ticket(self, ctx):
        """
        🎫 Создать тикет для обращения к администрации
        
        Использование:
        !ticket
        """
        try:
            # Создаём категорию для тикетов
            category = discord.utils.get(ctx.guild.categories, name="Тикеты")
            if not category:
                category = await ctx.guild.create_category(
                    name="Тикеты",
                    overwrites={
                        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
                    }
                )

            # Создаём канал тикета
            channel = await ctx.guild.create_text_channel(
                f'ticket-{ctx.author.name}',
                category=category,
                overwrites={
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    ctx.author: discord.PermissionOverwrite(read_messages=True),
                    ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
                }
            )

            embed = self.style.info_embed(
                "Тикет создан",
                f"{self.style.EMOJIS['ticket']} Ваш тикет создан: {channel.mention}\n"
                f"Для закрытия используйте `!close`"
            )
            embed.add_field(name="Автор", value=ctx.author.mention)
            embed.add_field(name="ID тикета", value=channel.id)
            
            await channel.send(embed=embed)
            await ctx.send(embed=self.style.success_embed("Успех", f"Тикет создан: {channel.mention}"))

        except Exception as e:
            await ctx.send(embed=self.style.error_embed("Ошибка", str(e)))

    @commands.command()
    async def close(self, ctx):
        """
        🔒 Закрыть текущий тикет
        
        Использование:
        !close
        """
        if 'ticket-' in ctx.channel.name:
            embed = self.style.warning_embed(
                "Закрытие тикета",
                f"{self.style.EMOJIS['lock']} Тикет будет закрыт через 5 секунд..."
            )
            await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await ctx.channel.delete()
        else:
            await ctx.send(embed=self.style.error_embed("Ошибка", "Эта команда работает только в каналах тикетов!"))

async def setup(bot):
    await bot.add_cog(Tickets(bot)) 