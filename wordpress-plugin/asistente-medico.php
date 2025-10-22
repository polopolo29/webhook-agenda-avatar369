<?php
/**
 * Plugin Name: Asistente Médico por PDF
 * Description: Un plugin que integra un asistente médico virtual basado en PDFs a través de un shortcode.
 * Version: 1.0
 * Author: Jules
 */

// Evitar acceso directo al archivo
if (!defined('ABSPATH')) {
    exit;
}

// URL del backend de Flask. ¡Asegúrate de que esta URL sea accesible desde tu servidor de WordPress!
define('ASISTENTE_API_URL', 'http://127.0.0.1:5001');

// Función para registrar los scripts y estilos
function asistente_medico_enqueue_assets() {
    // Solo encolar los assets si el shortcode está presente en la página actual
    global $post;
    if (is_a($post, 'WP_Post') && has_shortcode($post->post_content, 'asistente_medico_pdf')) {
        // Registrar el script de JS
        wp_enqueue_script(
            'asistente-medico-js',
            plugin_dir_url(__FILE__) . 'asistente-medico.js',
            array('jquery'), // Dependencia de jQuery
            '1.0',
            true // Cargar en el footer
        );

        // Pasar la URL de la API a nuestro script de JS
        wp_localize_script('asistente-medico-js', 'asistenteMedico', array(
            'apiUrl' => ASISTENTE_API_URL
        ));

        // Registrar el archivo de CSS
        wp_enqueue_style(
            'asistente-medico-css',
            plugin_dir_url(__FILE__) . 'asistente-medico.css',
            array(),
            '1.0'
        );
    }
}
add_action('wp_enqueue_scripts', 'asistente_medico_enqueue_assets');

// Función que define el shortcode
function asistente_medico_shortcode() {
    // El HTML de la interfaz del chat
    ob_start(); // Iniciar buffer de salida para capturar el HTML
    ?>
    <div id="asistente-medico-chat-container">
        <div id="asistente-medico-messages">
            <div class="asistente-medico-message asistente-medico-message-bot">
                <p>Iniciando conexión con el asistente...</p>
            </div>
        </div>
        <div id="asistente-medico-input-area">
            <form id="asistente-medico-form">
                <input type="text" id="asistente-medico-input" placeholder="Escribe tu respuesta aquí..." autocomplete="off" disabled>
                <button type="submit" id="asistente-medico-submit" disabled>Enviar</button>
            </form>
        </div>
    </div>
    <?php
    return ob_get_clean(); // Devolver el HTML capturado
}
add_shortcode('asistente_medico_pdf', 'asistente_medico_shortcode');
