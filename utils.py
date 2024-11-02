from flask import session, redirect, url_for
from functools import wraps
from models import User
import logging

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)

def get_current_user():
    """
    Obtiene el usuario actual a partir de la sesión.
    
    Returns:
        User: el usuario actual si está autenticado; de lo contrario, None.
    """
    user_id = session.get('user_id')
    if not user_id:
        logging.warning("get_current_user() - No hay user_id en la sesión.")
        return None

    # Consulta en la base de datos para obtener el usuario
    user = User.query.get(user_id)
    if user:
        logging.info(f"get_current_user() - Usuario encontrado: {user.username}")
        return user
    else:
        logging.error(f"get_current_user() - No se encontró un usuario con id: {user_id}")
        return None

def login_required(func):
    """
    Decorador para verificar si el usuario está autenticado antes de ejecutar la función.
    
    Args:
        func (function): La función que requiere autenticación.
    
    Returns:
        function: La función decorada que redirige al login si el usuario no está autenticado.
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not get_current_user():
            logging.warning("login_required() - Usuario no autenticado, redirigiendo al inicio de sesión.")
            return redirect(url_for('login'))  # Cambia 'login' si tienes otra ruta de autenticación
        return func(*args, **kwargs)

    return decorated_view
