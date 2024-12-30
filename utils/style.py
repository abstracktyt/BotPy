from discord import Embed, Color
import random

class Style:
    # Основные цвета
    COLORS = {
        'success': Color.green(),
        'error': Color.red(),
        'info': Color.blue(),
        'warning': Color.orange(),
        'purple': Color.purple(),
        'teal': Color.teal(),
        'random': lambda: Color.from_rgb(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
    }
    
    # Эмодзи
    EMOJIS = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'mod': '🛡️',
        'stats': '📊',
        'ticket': '🎫',
        'lock': '🔒',
        'unlock': '🔓',
        'settings': '⚙️',
        'members': '👥',
        'online': '🟢',
        'offline': '⚫',
        'loading': '🔄'
    }

    # Стили эмбедов
    STYLES = {
        'default': {
            'color': COLORS['info'],
            'emoji': EMOJIS['info']
        },
        'success': {
            'color': COLORS['success'],
            'emoji': EMOJIS['success']
        },
        'error': {
            'color': COLORS['error'],
            'emoji': EMOJIS['error']
        },
        'warning': {
            'color': COLORS['warning'],
            'emoji': EMOJIS['warning']
        },
        'mod': {
            'color': COLORS['purple'],
            'emoji': EMOJIS['mod']
        },
        'stats': {
            'color': COLORS['teal'],
            'emoji': EMOJIS['stats']
        }
    }

    def create_embed(self, style='default', title=None, description=None, **kwargs):
        style_data = self.STYLES.get(style, self.STYLES['default'])
        
        if title and not title.startswith(style_data['emoji']):
            title = f"{style_data['emoji']} {title}"
            
        embed = Embed(
            title=title,
            description=description,
            color=style_data['color']() if callable(style_data['color']) else style_data['color']
        )
        
        # Добавляем дополнительные поля
        for key, value in kwargs.items():
            if key == 'fields':
                for field in value:
                    embed.add_field(**field)
            elif key == 'footer':
                embed.set_footer(text=value)
            elif key == 'thumbnail':
                embed.set_thumbnail(url=value)
            elif key == 'image':
                embed.set_image(url=value)
            elif key == 'author':
                embed.set_author(**value)
                
        return embed

    def success_embed(self, title, description=None, **kwargs):
        return self.create_embed('success', title, description, **kwargs)

    def error_embed(self, title, description=None, **kwargs):
        return self.create_embed('error', title, description, **kwargs)

    def warning_embed(self, title, description=None, **kwargs):
        return self.create_embed('warning', title, description, **kwargs)

    def info_embed(self, title, description=None, **kwargs):
        return self.create_embed('info', title, description, **kwargs)

    def mod_embed(self, title, description=None, **kwargs):
        return self.create_embed('mod', title, description, **kwargs)

    def stats_embed(self, title, description=None, **kwargs):
        return self.create_embed('stats', title, description, **kwargs)

    def random_embed(self, title, description=None, **kwargs):
        return self.create_embed('random', title, description, **kwargs) 