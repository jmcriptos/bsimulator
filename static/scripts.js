document.addEventListener('DOMContentLoaded', function() {
    var socket = io();

    // Enviar mensaje de chat
    document.getElementById('chatMessage').addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    document.querySelector('#chat button').addEventListener('click', sendMessage);

    function sendMessage() {
        var message = document.getElementById('chatMessage').value;
        if (message.trim() !== "") {
            socket.emit('send_message', { user_id: user_id, team: team, message: message });
            document.getElementById('chatMessage').value = '';
        }
    }

    // Recibir mensaje de chat
    socket.on('receive_message', function(data) {
        var chatBox = document.getElementById('chatBox');
        var newMessage = document.createElement('p');
        newMessage.innerHTML = '<strong>' + data.user_id + ':</strong> ' + data.message;
        chatBox.appendChild(newMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
        document.getElementById('chatMessage').focus();
    });

    // Enviar decisiones del formulario
    document.querySelector('#decisionForm form').addEventListener('submit', function(event) {
        event.preventDefault();
        sendDecision();
    });

    function sendDecision() {
        var price = parseFloat(document.getElementById('price').value);
        var marketing = parseFloat(document.getElementById('marketing').value);
        var quality = parseFloat(document.getElementById('quality').value);
        var production = parseFloat(document.getElementById('production').value);
        var innovation = parseFloat(document.getElementById('innovation').value);
    
        console.log('Preparando para enviar decisión:', { price, marketing, quality, production, innovation });
    
        if (!isNaN(price) && !isNaN(marketing) && !isNaN(quality) && !isNaN(production) && !isNaN(innovation)) {
            socket.emit('send_decision', {
                team: team,
                price: price,
                marketing: marketing,
                quality: quality,
                production: production,
                innovation: innovation
            });
            console.log('Decisión enviada:', { team, price, marketing, quality, production, innovation });
        } else {
            console.error('Error: Campos no válidos.');
            alert('Por favor, complete todos los campos con valores numéricos antes de enviar la decisión.');
        }
    }

    socket.on('show_results', function() {
        window.location.href = '/results';
    });
    

    // Recibir confirmación de envío de decisiones
    socket.on('decision_received', function(data) {
        console.log('Decisión recibida por el servidor:', data);
        window.location.href = '/results';  // Redirigir a resultados
    });
    

    // Foco automático en el campo del mensaje después de enviar
    document.getElementById('chatMessage').focus();
});


