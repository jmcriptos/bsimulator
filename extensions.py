# extensions.py
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# Instancias de extensiones
socketio = SocketIO(cors_allowed_origins="*")
db = SQLAlchemy()


