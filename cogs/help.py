import discord
from discord.ext import commands
from utils.style import Style

class CustomHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.style = Style()
        bot.remove_command('help')  # Удаляем стандартную команду help

    @commands.command()
    async def help(self, ctx, command=None):
        """
        📚 Показать список всех команд и их описание
        
        Использование:
        !help [команда]
        """
        if command is None:
            # Создаем главное меню помощи
            embed = self.style.info_embed(
                "📚 Справочник команд",
                "Используйте `!help <команда>` для подробной информации о команде"
            )

            # Модерация
            mod_commands = [
                f"{self.style.EMOJIS['ban']} `!ban` - Забанить участника",
                f"{self.style.EMOJIS['kick']} `!kick` - Выгнать участника",
                f"{self.style.EMOJIS['mute']} `!mute` - Замутить участника",
                f"🧹 `!clear` - Очистить сообщения"
            ]
            embed.add_field(
                name=f"{self.style.EMOJIS['mod']} Модерация",
                value="\n".join(mod_commands),
                inline=False
            )

            # Тикеты
            ticket_commands = [
                f"{self.style.EMOJIS['ticket']} `!ticket` - Создать тикет",
                f"{self.style.EMOJIS['lock']} `!close` - Закрыть тикет"
            ]
            embed.add_field(
                name="🎫 Система тикетов",
                value="\n".join(ticket_commands),
                inline=False
            )

            # Статистика
            stats_commands = [
                f"{self.style.EMOJIS['stats']} `!stats` - Статистика сервера"
            ]
            embed.add_field(
                name="📊 Статистика",
                value="\n".join(stats_commands),
                inline=False
            )

            # Голосования
            poll_commands = [
                f"{self.style.EMOJIS['poll']} `!poll` - Создать голосование"
            ]
            embed.add_field(
                name="📊 Голосования",
                value="\n".join(poll_commands),
                inline=False
            )

            # Анти-слив
            antileak_commands = [
                f"{self.style.EMOJIS['shield']} `!antileak` - Управление защитой",
                f"{self.style.EMOJIS['settings']} `!raidlimits` - Настройки защиты"
            ]
            embed.add_field(
                name="🛡️ Защита сервера",
                value="\n".join(antileak_commands),
                inline=False
            )

            embed.set_footer(text="Бот разработан с ❤️")

        else:
            # Показываем информацию о конкретной команде
            cmd = self.bot.get_command(command)
            if cmd is None:
                await ctx.send(embed=self.style.error_embed(
                    "Ошибка",
                    f"Команда `{command}` не найдена!"
                ))
                return

            embed = self.style.info_embed(
                f"📚 Справка по команде: {cmd.name}",
                cmd.help or "Описание отсутствует"
            )
            
            # Добавляем информацию об использовании
            if cmd.usage:
                embed.add_field(
                    name="Использование",
                    value=f"`{cmd.usage}`",
                    inline=False
                )

            # Добавляем информацию о правах
            if cmd.checks:
                permissions = []
                for check in cmd.checks:
                    if hasattr(check, 'permissions'):
                        permissions.extend(check.permissions)
                if permissions:
                    embed.add_field(
                        name="Необходимые права",
                        value="\n".join(f"• {perm}" for perm in permissions),
                        inline=False
                    )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomHelp(bot)) 