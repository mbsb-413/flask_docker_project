from flask import Flask, render_template, jsonify, request
from models import db, User, Message
import os
import datetime

app = Flask(__name__)

# Конфигурация базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/flaskdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Инициализация базы данных
db.init_app(app)

@app.route('/')
def home():
    # Получаем данные из базы
    users_count = User.query.count()
    messages_count = Message.query.count()
    recent_messages = Message.query.order_by(Message.created_at.desc()).limit(5).all()
    
    return render_template('index.html',
                         server_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         users_count=users_count,
                         messages_count=messages_count,
                         recent_messages=recent_messages)

@app.route('/api/stats')
def api_stats():
    stats = {
        'status': 'running',
        'timestamp': datetime.datetime.now().isoformat(),
        'database': {
            'users': User.query.count(),
            'messages': Message.query.count(),
            'connected': True
        },
        'services': {
            'flask': 'running',
            'postgres': 'connected',
            'nginx': 'optional'
        }
    }
    return jsonify(stats)

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    } for user in users])

@app.route('/api/messages', methods=['GET', 'POST'])
def handle_messages():
    if request.method == 'POST':
        data = request.json
        new_message = Message(
            user_id=data.get('user_id', 1),
            message=data.get('message', '')
        )
        db.session.add(new_message)
        db.session.commit()
        return jsonify({'status': 'success', 'message_id': new_message.id})
    
    # GET запрос
    messages = Message.query.order_by(Message.created_at.desc()).limit(10).all()
    return jsonify([{
        'id': msg.id,
        'user_id': msg.user_id,
        'message': msg.message,
        'created_at': msg.created_at.isoformat(),
        'author': msg.author.username if msg.author else 'Unknown'
    } for msg in messages])

@app.route('/admin')
def admin_panel():
    return render_template('index.html', section='admin')

# Создание таблиц при первом запуске
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
