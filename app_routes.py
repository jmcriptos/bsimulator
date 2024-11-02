from flask import render_template, redirect, url_for, request, session, jsonify
from models import db
from utils import get_current_user
from flask_socketio import join_room, emit
from forms import JoinForm  # Asegúrate de importar JoinForm aquí
from extensions import socketio  # Importar socketio de extensions

# Diccionarios de equipos y resultados
teams = {'Equipo A': [], 'Equipo B': []}
game_results = {
    "Equipo A": {"Demand": 0, "Profit": 0, "Cash": 0},
    "Equipo B": {"Demand": 0, "Profit": 0, "Cash": 0}
}

# Diccionario para rastrear si los equipos ya enviaron sus decisiones
teams_ready = {
    "Equipo A": False,
    "Equipo B": False
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
        return render_template('game.html', user_id=user_id, team=team, teams=teams, game_results=game_results)

    @app.route('/results')
    def show_results():
        return render_template('results.html', results=game_results)

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        session.pop('team', None)
        return redirect(url_for('index'))

    @socketio.on('send_decision')
    def handle_send_decision(data):
        # Obtener el equipo al que pertenece el usuario desde los datos recibidos
        team = data.get('team')
        price = data.get('price', 0)
        marketing = data.get('marketing', 0)
        quality = data.get('quality', 0)
        production = data.get('production', 0)
        innovation = data.get('innovation', 0)
        
        # Validar que el equipo esté registrado
        if team not in game_results:
            return  # Si el equipo no está registrado, salir de la función

        # Lógica de cálculo de demanda y profit
        demand_influence = max(0, 10 - price) + marketing * 0.1 + quality * 0.5 + innovation * 0.3
        demand = int(demand_influence * 100)
        actual_sales = min(production, demand)  # Las ventas reales están limitadas por la producción y la demanda
        revenue = price * actual_sales  # Los ingresos dependen de las ventas reales
        costs = (production * 0.8) + (marketing * 1.2) + (innovation * 1.5)
        profit = revenue - costs
        
        # Actualizar resultados del equipo
        game_results[team]['Demand'] += demand
        game_results[team]['Profit'] += profit
        game_results[team]['Cash'] += profit  # Asumiendo que el profit incrementa el cash disponible

        # Marcar al equipo como listo
        teams_ready[team] = True

        # Verificar si ambos equipos están listos
        if all(teams_ready.values()):
            # Resetear el estado para la siguiente ronda
            teams_ready["Equipo A"] = False
            teams_ready["Equipo B"] = False

            # Emitir los resultados actualizados a todos los clientes
            emit('display_results', {
                'results': game_results,
            }, broadcast=True)

    @socketio.on('send_message')
    def handle_send_message(data):
        print(f"Mensaje recibido: {data}")
        user_id = data['user_id']
        team = data['team']
        message = data['message']

        # Emitir el mensaje a todos los miembros del equipo
        emit('receive_message', {
            'user_id': user_id,
            'message': message
        }, room=team)

    @socketio.on('join')
    def on_join(data):
        user_id = data.get('user_id')
        team = data.get('team')
        
        # Unirse a la sala correspondiente
        join_room(team)

        # Enviar una notificación al equipo
        emit('team_notification', {'message': f'{user_id} se ha unido al equipo {team}'}, room=team)

    @socketio.on('disconnect')
    def on_disconnect():
        # Desconectar al usuario y removerlo del equipo
        user_id = session.get('user_id')
        team = session.get('team')
        if user_id and team and user_id in teams[team]:
            teams[team].remove(user_id)
            emit('team_notification', {'message': f'{user_id} ha salido del equipo {team}'}, room=team)
