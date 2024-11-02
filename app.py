from flask import Flask, render_template, session, redirect, url_for
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO
from forms import JoinForm
import app_routes

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esto por una clave secreta segura
csrf = CSRFProtect(app)  # Inicializar CSRF protection
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")  # Habilitar SocketIO

# Registrar las rutas de la aplicación desde app_routes
app_routes.register_routes(app)

# Ejecución de la aplicación con soporte de SocketIO
if __name__ == '__main__':
    socketio.run(app)

