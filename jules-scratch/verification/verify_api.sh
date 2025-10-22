#!/bin/bash
# Script to verify the backend API by simulating a full conversation.

API_URL="http://127.0.0.1:5000/chat"
LOG_FILE="jules-scratch/verification/conversation_transcript.log"
SESSION_ID=""

# Function to send a message and log the response
send_message() {
    local message=$1
    echo "User: $message" >> $LOG_FILE

    response=$(curl -s -X POST $API_URL \
        -H "Content-Type: application/json" \
        -d @- << EOF
{
    "session_id": "$SESSION_ID",
    "message": "$message"
}
EOF
    )

    # Update session_id if it's the first message
    if [ -z "$SESSION_ID" ]; then
        SESSION_ID=$(echo $response | jq -r .session_id)
    fi

    bot_response=$(echo $response | jq -r .response)
    echo "Bot: $bot_response" >> $LOG_FILE
    echo "---------------------------------" >> $LOG_FILE
    sleep 1 # Add a 1-second delay to prevent race conditions
}

# Clear previous log
> $LOG_FILE

echo "Starting API verification..."

# 1. Start conversation
send_message "Hola"
# 2. Answer questions
send_message "Juan Perez"
send_message "35"
send_message "1.75m, 80kg"
send_message "Mexicana"
send_message "Dolor de cabeza y fatiga"
send_message "Diabetes, desde hace 2 años"
send_message "Cansancio y visión borrosa"
send_message "si"
send_message "Metformina"
send_message "Trigo y azúcar"
# 3. Proceed through the 6 protocol steps
send_message "sí" # Causa del Origen
send_message "sí" # Protocolo Espiritual
send_message "sí" # Protocolo Específico
send_message "sí" # Dieta
send_message "sí" # Ejercicio
send_message "sí" # Productos Naturales

echo "Verification complete. Transcript saved to $LOG_FILE"
