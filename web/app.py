from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, 
    login_required, 
    current_user, 
    UserMixin, 
    login_user, 
    logout_user
)
import discord
from discord.ext import commands
from discord import app_commands
import os
import requests
from datetime import datetime, timedelta
import json
from os import getenv
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv('DISCORD_TOKEN')

# Конфигурация Discord OAuth2
DISCORD_CLIENT_ID = '1262763058791583865'  # Замените на ваш Client ID
DISCORD_CLIENT_SECRET = 'BsyTABcb2LOVDTjKaUuqApHuEpsEHUra'  # Замените на ваш Client Secret
DISCORD_REDIRECT_URI = 'http://localhost:5000/callback'
DISCORD_BOT_TOKEN = 'your_discord_bot_token'  # Замените на ваш токен бота

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# Правильный путь к базе данных
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Модели
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(20), unique=True)
    username = db.Column(db.String(100))
    avatar = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    access_token = db.Column(db.String(100))
    refresh_token = db.Column(db.String(100))

    def get_id(self):
        return str(self.id)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.String(20))
    channel_id = db.Column(db.String(20))
    creator_id = db.Column(db.String(20))
    subject = db.Column(db.String(100))
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(20))  # BOT, PANEL, ERROR, TICKET
    action = db.Column(db.String(100))
    details = db.Column(db.Text)
    user_id = db.Column(db.String(20), nullable=True)
    guild_id = db.Column(db.String(20), nullable=True)

def add_log(type, action, details=None, user_id=None, guild_id=None):
    log = Log(
        type=type,
        action=action,
        details=details,
        user_id=user_id,
        guild_id=guild_id
    )
    db.session.add(log)
    db.session.commit()
    socketio.emit('new_log', {
        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'type': log.type,
        'action': log.action,
        'details': log.details
    })

# Инициализация Discord бота
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Команды бота
@bot.tree.command(name="ticket", description="Создать тикет")
@app_commands.describe(subject="Тема тикета")
async def ticket(interaction: discord.Interaction, subject: str):
    await interaction.response.send_message(f"Создание тикета: {subject}")

@bot.tree.command(name="stats", description="Показать статистику")
async def stats(interaction: discord.Interaction):
    await interaction.response.send_message("Статистика бота")

@bot.event
async def on_ready():
    print(f'Бот {bot.user} готов к работе!')
    add_log('BOT', 'Startup', f'Bot {bot.user} is ready')
    await bot.tree.sync()
    print("Команды синхронизированы!")

@bot.event
async def on_guild_join(guild):
    add_log('BOT', 'Guild Join', f'Joined {guild.name}', guild_id=str(guild.id))

@bot.event
async def on_guild_remove(guild):
    add_log('BOT', 'Guild Leave', f'Left {guild.name}', guild_id=str(guild.id))

# Flask routes
@app.route('/login')
def login():
    return redirect(f'https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify%20guilds')

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post('https://discord.com/api/oauth2/token', data=data, headers=headers)
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get('https://discord.com/api/users/@me', headers=headers)
        user_data = user_response.json()

        user = User.query.filter_by(discord_id=user_data['id']).first()
        if not user:
            user = User(
                discord_id=user_data['id'],
                username=user_data['username'],
                avatar=f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png" if user_data['avatar'] else None,
                access_token=access_token,
                refresh_token=tokens.get('refresh_token')
            )
            db.session.add(user)
        else:
            user.access_token = access_token
            user.refresh_token = tokens.get('refresh_token')
        
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    
    return 'Ошибка авторизации', 400

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/stats')
@login_required
def stats():
    # Получаем номер страницы из параметров запроса
    page = request.args.get('page', 1, type=int)
    
    # Получаем даты за последние 7 дней
    dates = [(datetime.now() - timedelta(days=i)).strftime('%d.%m') for i in range(6, -1, -1)]
    
    # Получаем логи по дням
    activity_counts = [
        Log.query.filter(
            Log.timestamp >= datetime.now() - timedelta(days=i+1),
            Log.timestamp < datetime.now() - timedelta(days=i)
        ).count()
        for i in range(6, -1, -1)
    ]

    # Получаем логи с пагинацией
    logs_pagination = Log.query.order_by(Log.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    stats_data = {
        'total_users': sum(g.member_count for g in bot.guilds),
        'total_servers': len(bot.guilds),
        'total_tickets': Ticket.query.count(),
        'open_tickets': Ticket.query.filter_by(status='open').count()
    }

    return render_template('stats.html', 
                         stats=stats_data,
                         activity_dates=dates,
                         activity_counts=activity_counts,
                         logs=logs_pagination.items,
                         pagination=logs_pagination)

@app.route('/tickets')
@login_required
def tickets():
    all_tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return render_template('tickets.html', tickets=all_tickets)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Создание базы данных
with app.app_context():
    db.create_all()
    print("База данных создана")
    # Создаем админа если его нет
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            discord_id='ВАШ_DISCORD_ID',
            username='Admin',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Администратор создан")

def run_bot():
    bot.run(DISCORD_BOT_TOKEN)

@app.route('/logs')
@login_required
def logs():
    page = request.args.get('page', 1, type=int)
    log_type = request.args.get('type')
    
    query = Log.query
    if log_type:
        query = query.filter_by(type=log_type)
    
    logs_pagination = query.order_by(Log.timestamp.desc()).paginate(
        page=page, per_page=50
    )
    
    return render_template('logs.html', logs=logs_pagination.items, pagination=logs_pagination)

@app.route('/api/logs')
@login_required
def api_logs():
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    logs = Log.query.filter(Log.timestamp >= start_date).all()
    data = {
        'labels': [],
        'bot': [],
        'panel': [],
        'ticket': [],
        'error': []
    }
    
    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        data['labels'].append(date)
        data['bot'].append(0)
        data['panel'].append(0)
        data['ticket'].append(0)
        data['error'].append(0)
    
    for log in logs:
        day_index = (log.timestamp - start_date).days
        if 0 <= day_index < days:
            data[log.type.lower()][day_index] += 1
    
    return jsonify(data)

if __name__ == '__main__':
    import threading
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    socketio.run(app, debug=True) 