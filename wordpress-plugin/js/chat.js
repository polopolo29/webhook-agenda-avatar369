jQuery(document).ready(function($) {
    const chatBox = $('#chat-box');
    const chatInput = $('#chat-input');
    const chatSend = $('#chat-send');

    let sessionId = null;

    function addMessage(message, sender) {
        const messageClass = sender === 'user' ? 'user-message' : 'bot-message';
        const messageElement = $(`<div></div>`).addClass('chat-message').addClass(messageClass).text(message);
        chatBox.append(messageElement);
        chatBox.scrollTop(chatBox[0].scrollHeight); // Auto-scroll to the bottom
    }

    async function sendMessage() {
        const message = chatInput.val().trim();
        if (!message) return;

        addMessage(message, 'user');
        chatInput.val('');

        try {
            const response = await $.ajax({
                url: chat_settings.api_url,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    session_id: sessionId,
                    message: message
                })
            });

            sessionId = response.session_id; // Store the session ID
            addMessage(response.response, 'bot');

        } catch (error) {
            console.error("Error communicating with the chat backend:", error);
            addMessage("Lo siento, no puedo conectarme con el asistente en este momento.", 'bot');
        }
    }

    // Event listeners
    chatSend.on('click', sendMessage);
    chatInput.on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            sendMessage();
        }
    });

    // Initial greeting from the bot
    async function startConversation() {
        try {
            const response = await $.ajax({
                url: chat_settings.api_url,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    session_id: null, // Start a new session
                    message: "Hola" // Initial message to kickstart the questionnaire
                })
            });

            sessionId = response.session_id;
            addMessage(response.response, 'bot');
        } catch (error) {
            console.error("Error starting conversation:", error);
            addMessage("Error al iniciar. Por favor, recarga la página.", 'bot');
        }
    }

    startConversation();
});
