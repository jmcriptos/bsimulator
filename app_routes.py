from flask import render_template, redirect, url_for, request, session, jsonify
from models import db
from utils import get_current_user
from flask_socketio import join_room, emit
from forms import JoinForm  # Asegúrate de importar JoinForm aquí
from extensions import socketio  # Importar socketio de extensions

# Diccionarios de equipos y resultados
teams = {'Equipo A': [], 'Equipo B': []}
game_results = {
    "Equipo A": {"Demand": 0, "Profit": 0, "Cash": 50000, "Inventory": 0},
    "Equipo B": {"Demand": 0, "Profit": 0, "Cash": 50000, "Inventory": 0}
}

decisiones = {}  # Diccionario para almacenar decisiones de los equipos
teams_ready = {
    "Equipo A": False,
    "Equipo B": False
}

current_round = 0  # Variable global para controlar la ronda actual

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
        ronda_actual = f"ronda_{current_round}"  # Utiliza la ronda actual global
        return render_template('game.html', user_id=user_id, team=team, teams=teams, game_results=game_results, ronda_actual=ronda_actual)

    
    @app.route('/results')
    def show_results():
        try:
            results = calcular_resultados(decisiones)
            return render_template('results.html', resultados=results)
        except Exception as e:
            print("Error al calcular los resultados:", e)
            return "Error al calcular los resultados.", 500


    @app.route('/start_new_round', methods=['POST'])
    def start_new_round():
        global current_round
        # Solo permitir una nueva ronda cuando ambas decisiones hayan sido enviadas
        if all(teams_ready.values()):
            # Incrementar la ronda actual
            current_round += 1

            # Reiniciar las decisiones de los equipos para la nueva ronda
            ronda_actual = f'ronda_{current_round}'
            decisiones[ronda_actual] = {}

            # Reiniciar el estado de los equipos listos
            teams_ready["Equipo A"] = False
            teams_ready["Equipo B"] = False

        return redirect(url_for('game'))

@socketio.on('start_new_round')
def handle_start_new_round():
    global current_round
    print("Nueva ronda iniciada por un equipo")
    # Solo permitir una nueva ronda cuando ambas decisiones hayan sido enviadas
    if all(teams_ready.values()):
        # Incrementar la ronda actual
        current_round += 1

        # Reiniciar las decisiones de los equipos para la nueva ronda
        ronda_actual = f'ronda_{current_round}'
        decisiones[ronda_actual] = {}

        # Reiniciar el estado de los equipos listos
        teams_ready["Equipo A"] = False
        teams_ready["Equipo B"] = False

        # Emitir el evento de nueva ronda iniciada
        socketio.emit('new_round_started')

@socketio.on('send_decision')
def handle_decision(data):
    print('Decision received:', data)  # Añade este print para ver si la decisión es recibida
    emit('decision_received', data, broadcast=True)

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

    # Registrar la decisión
    ronda_actual = f'ronda_{current_round}'
    if ronda_actual not in decisiones:
        decisiones[ronda_actual] = {}
    decisiones[ronda_actual][team] = {
        'price': price,
        'marketing': marketing,
        'quality': quality,
        'production': production,
        'innovation': innovation
    }

    # Marcar al equipo como listo
    teams_ready[team] = True

    # Verificar si ambos equipos están listos
    if all(teams_ready.values()):
        # Emitir los resultados actualizados a todos los clientes
        socketio.emit('display_results', {
           'results': calcular_resultados(decisiones)
        }, namespace='/', to=None)

        # Emitir evento para redirigir a la página de resultados
        socketio.emit('show_results')  # Removido 'room=team' para asegurarse que todos los usuarios reciban el evento

        print("Evento 'show_results' emitido para todos los clientes.")

@socketio.on('reset_game')
def handle_reset_game():
    global current_round
    print("Reiniciando el juego a la ronda cero")
    # Reiniciar todas las variables a su estado inicial
    current_round = 0
    global decisiones, game_results, teams_ready, teams
    decisiones = {}
    game_results = {
        "Equipo A": {"Demand": 0, "Profit": 0, "Cash": 50000, "Inventory": 20000},
        "Equipo B": {"Demand": 0, "Profit": 0, "Cash": 50000, "Inventory": 20000}
    }
    teams_ready = {
        "Equipo A": False,
        "Equipo B": False
    }
    teams = {'Equipo A': [], 'Equipo B': []}

    # Emitir el evento de reinicio de juego
    socketio.emit('game_reset')


def calcular_resultados(decisiones):
    """
    Calcula los resultados del simulador de negocios en función de las decisiones tomadas por cada equipo.

    Args:
        decisiones (dict): Diccionario con las decisiones de cada equipo. Debe contener la información de cada ronda,
                        como el precio, marketing, calidad, producción e innovación.

    Returns:
        dict: Resultados calculados para cada equipo, con la demanda, ganancia, efectivo e inventario.
    """
    resultados = {}

    for ronda, equipos in decisiones.items():
        resultados[ronda] = {}

        for equipo, decision in equipos.items():
            # Inventario disponible al inicio de la ronda
            inventario_inicial = game_results[equipo]['Inventory']
            produccion = decision['production']
            inventario_disponible = inventario_inicial + produccion

            # Calcula la demanda (un ejemplo simple basado en el precio, marketing y ahora innovación)
            demanda = max(0, 10000 - decision['price'] * 100 + decision['marketing'] * 2 + decision['quality'] * 50 + decision['innovation'] * 10)

            # Ajustar la demanda para que no exceda el inventario disponible
            ventas_reales = min(demanda, inventario_disponible)

            # Calcula los ingresos como el producto de las ventas reales y el precio
            ingresos = ventas_reales * decision['price']

            # Costo de ventas (considerando el costo del 50% del precio para las unidades vendidas)
            costo_ventas = ventas_reales * decision['price'] * 0.50

            # Costos de marketing e innovación
            costos_marketing_innovacion = decision['marketing'] + decision['innovation']

            # Calcular variación del inventario
            variacion_inventario = inventario_disponible - ventas_reales

            # Si el inventario aumentó, debemos considerar el costo de almacenamiento (supongamos que es un 10% del valor de producción)
            # Si el inventario disminuyó, se considera que ya está cubierto por el costo de producción
            costo_inventario = 0
            if variacion_inventario > inventario_inicial:
                costo_inventario = (variacion_inventario - inventario_inicial) * decision['price'] * 0.10

            # Calcula la ganancia: ingresos menos los costos
            ganancia = ingresos - costo_ventas - costos_marketing_innovacion - costo_inventario

            # Actualizar inventario (restar las ventas reales de lo disponible)
            inventario = inventario_disponible - ventas_reales

            # Calcula el efectivo restante considerando la ganancia y los costos de marketing, innovación e inventario
            efectivo_restante = game_results[equipo]['Cash'] + ganancia

            # Almacena los resultados
            resultados[ronda][equipo] = {
                'Demand': demanda,
                'Profit': ganancia,
                'Cash': efectivo_restante,
                'Inventory': inventario,
                'Decisions': decision
            }

            # Actualizar los resultados del equipo en el diccionario global
            game_results[equipo]['Demand'] = demanda
            game_results[equipo]['Profit'] = ganancia
            game_results[equipo]['Cash'] = efectivo_restante
            game_results[equipo]['Inventory'] = inventario

    return resultados





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














