from flask import Flask
from flask_wtf import CSRFProtect
from forms import JoinForm
from extensions import socketio  # Import socketio from extensions
import eventlet  # Use eventlet for improved WebSocket handling

# Configuración de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'a31724589z'  # Usa una clave segura y constante para el desarrollo.

# Proteger la aplicación contra CSRF
csrf = CSRFProtect(app)

# Inicializa socketio con la aplicación Flask usando eventlet para evitar errores
socketio.init_app(app, async_mode='gevent')  # Use 'eventlet' async_mode for compatibility

# Registrar las rutas de la aplicación después de la configuración
import app_routes
app_routes.register_routes(app)

# Ejecución de la aplicación con soporte de SocketIO
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)  # Añadido puerto y debug para desarrollo


