from flask import render_template, redirect, url_for, request, session, jsonify
from models import db
from utils import get_current_user
from flask_socketio import join_room, emit
from app import socketio
from forms import JoinForm  # Asegúrate de importar JoinForm aquí

# Diccionarios de equipos y resultados
teams = {'Equipo A': [], 'Equipo B': []}
game_results = {
    "Equipo A": {"Demand": 0, "Profit": 0, "Cash": 0},
    "Equipo B": {"Demand": 0, "Profit": 0, "Cash": 0}
}

def register_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = JoinForm()
        if form.validate_on_submit():
            user_id = form.user_id.data
            team = form.team.data
            
            # Guardar user_id y equipo en la sesión
            session['user_id'] = user_id
            session['team'] = team

            # Agregar usuario al equipo seleccionado si no está ya en él
            if user_id not in teams[team]:
                teams[team].append(user_id)

            return redirect(url_for('game'))

        # Mostrar la página inicial con el formulario
        return render_template('index.html', form=form, teams=teams)

    @app.route('/game')
    def game():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        user_id = session['user_id']
        team = session['team']
        return render_template('game.html', user_id=user_id, team=team, teams=teams)

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        session.pop('team', None)
        return redirect(url_for('index'))


