jQuery(document).ready(function($) {
    const messagesContainer = $('#asistente-medico-messages');
    const form = $('#asistente-medico-form');
    const input = $('#asistente-medico-input');
    const submitButton = $('#asistente-medico-submit');

    let sessionId = null;
    const apiUrl = asistenteMedico.apiUrl; // Obtenido del wp_localize_script

    // Función para añadir mensajes a la ventana del chat
    function addMessage(sender, text) {
        // Formatear saltos de línea y texto en negrita simple
        text = text.replace(/\\n/g, '<br>');
        text = text.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>'); // Para **texto**
        text = text.replace(/•/g, '<br>•'); // Salto de línea antes de viñetas

        const messageElement = $('<div class="asistente-medico-message"></div>');
        messageElement.addClass('asistente-medico-message-' + sender);
        messageElement.html(`<p>${text}</p>`);
        messagesContainer.append(messageElement);
        // Hacer scroll hasta el último mensaje
        messagesContainer.scrollTop(messagesContainer[0].scrollHeight);
    }

    // Función para habilitar/deshabilitar el formulario
    function setFormDisabled(disabled) {
        input.prop('disabled', disabled);
        submitButton.prop('disabled', disabled);
        if (!disabled) {
            input.focus();
        }
    }

    // 1. Iniciar la conversación al cargar
    function startChat() {
        $.ajax({
            url: `${apiUrl}/start`,
            type: 'GET',
            success: function(response) {
                sessionId = response.session_id;
                addMessage('bot', response.message);
                setFormDisabled(false);
            },
            error: function() {
                addMessage('bot', 'Error: No se pudo conectar con el asistente. Por favor, asegúrate de que el servidor backend esté en funcionamiento y la URL sea correcta.');
            }
        });
    }

    // 2. Manejar el envío de respuestas del usuario
    form.on('submit', function(event) {
        event.preventDefault();
        const userResponse = input.val();

        if (!userResponse.trim() || !sessionId) {
            return;
        }

        addMessage('user', userResponse);
        setFormDisabled(true);
        input.val('');

        // Enviar la respuesta al backend
        $.ajax({
            url: `${apiUrl}/interact`,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                session_id: sessionId,
                response: userResponse
            }),
            success: function(response) {
                addMessage('bot', response.message);
                // Si no es el final de la conversación, habilitar el input
                if (response.type !== 'final') {
                    setFormDisabled(false);
                }
            },
            error: function() {
                addMessage('bot', 'Error: Hubo un problema al procesar tu respuesta.');
                setFormDisabled(false);
            }
        });
    });

    // Iniciar el chat
    startChat();
});
