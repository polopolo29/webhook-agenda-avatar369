<?php
/**
 * Plugin Name: Asistente Médico PDF
 * Description: Añade un chat de asistente médico basado en PDFs a tu sitio de WordPress con el shortcode [asistente_medico_pdf].
 * Version: 1.0
 * Author: Jules
 */

if (!defined('ABSPATH')) {
    exit; // Exit if accessed directly.
}

// 1. Shortcode to display the chat interface
function asistente_medico_pdf_shortcode() {
    // The chat container will be rendered here.
    // The actual chat interface will be built by JavaScript.
    ob_start();
    ?>
    <div id="asistente-medico-chat-container">
        <div id="chat-box"></div>
        <input type="text" id="chat-input" placeholder="Escribe tu mensaje aquí...">
        <button id="chat-send">Enviar</button>
    </div>
    <?php
    return ob_get_clean();
}
add_shortcode('asistente_medico_pdf', 'asistente_medico_pdf_shortcode');

// 2. Enqueue scripts and styles for the chat
function asistente_medico_pdf_enqueue_assets() {
    // Only load assets if the shortcode is present on the page
    if (is_a(get_post(get_the_ID()), 'WP_Post') && has_shortcode(get_post(get_the_ID())->post_content, 'asistente_medico_pdf')) {
        // Enqueue custom CSS
        wp_enqueue_style(
            'asistente-medico-pdf-css',
            plugin_dir_url(__FILE__) . 'css/chat-style.css',
            [],
            '1.0'
        );

        // Enqueue custom JavaScript
        wp_enqueue_script(
            'asistente-medico-pdf-js',
            plugin_dir_url(__FILE__) . 'js/chat.js',
            ['jquery'], // Dependency
            '1.0',
            true // Load in footer
        );

        // Pass the backend URL to the JavaScript file
        wp_localize_script('asistente-medico-pdf-js', 'chat_settings', [
            'api_url' => 'http://127.0.0.1:5000/chat', // URL of the Flask backend
            'upload_url' => 'http://127.0.0.1:5000/upload-pdf' // URL for PDF uploads
        ]);
    }
}
add_action('wp_enqueue_scripts', 'asistente_medico_pdf_enqueue_assets');

// 3. Admin Menu for PDF Uploads
function asistente_medico_pdf_admin_menu() {
    add_menu_page(
        'Asistente Médico PDF',
        'Asistente PDF',
        'manage_options',
        'asistente-medico-pdf-admin',
        'asistente_medico_pdf_admin_page',
        'dashicons-book-alt'
    );
}
add_action('admin_menu', 'asistente_medico_pdf_admin_menu');

// 4. Admin Page Content
function asistente_medico_pdf_admin_page() {
    ?>
    <div class="wrap">
        <h1>Cargar PDFs para el Asistente Médico</h1>
        <p>Sube nuevos archivos PDF a la base de conocimiento del asistente. El sistema los cargará automáticamente.</p>

        <form id="pdf-upload-form" method="post" enctype="multipart/form-data">
            <input type="file" id="pdf_file" name="pdf_file" accept=".pdf" required>
            <input type="submit" name="submit_pdf" class="button button-primary" value="Subir PDF">
        </form>
        <div id="upload-status"></div>
    </div>

    <script>
    jQuery(document).ready(function($) {
        $('#pdf-upload-form').on('submit', function(e) {
            e.preventDefault();

            const fileInput = $('#pdf_file')[0];
            if (fileInput.files.length === 0) {
                $('#upload-status').text('Por favor, selecciona un archivo.');
                return;
            }

            const formData = new FormData();
            formData.append('pdf_file', fileInput.files[0]);

            $('#upload-status').text('Subiendo...');

            $.ajax({
                url: '<?php echo esc_js('http://127.0.0.1:5000/upload-pdf'); ?>',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    $('#upload-status').text('¡Éxito! El archivo "' + fileInput.files[0].name + '" ha sido subido.');
                    $('#pdf_file').val(''); // Clear the input
                },
                error: function(xhr, status, error) {
                    $('#upload-status').text('Error: ' + xhr.responseText);
                }
            });
        });
    });
    </script>
    <?php
}
