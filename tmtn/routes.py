import os
from flask import current_app, request, send_file, render_template, url_for
from flask_socketio import emit
from werkzeug.utils import secure_filename
import zipfile
from .helper import allowed_file, calculate_total_qty

def register_routes(app, socketio):
    @app.route('/')
    def main_page():
        return render_template('main.html')

    @app.route('/transfer_material_to_needed', methods=['GET', 'POST'])
    def transfer_material_to_needed():
        """Render the transfer_material_to_needed page."""
        return render_template('transfer_material_to_needed.html')

    @app.route('/transfer_orders_to_components', methods=['GET', 'POST'])
    def transfer_orders_to_components():
        """Render the transfer_orders_to_components page."""
        return render_template('transfer_orders_to_components.html')
    
    @app.route('/daily_matcher', methods=['GET', 'POST'])
    def daily_matcher():
        """Render the transfer_orders_to_components page."""
        return render_template('daily_matcher.html')
    
    @app.route('/download/<filename>')
    def download_file(filename):
        """Allow users to download processed files."""
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404

    @socketio.on('file_uploaded_tmtn')
    def handle_file_uploaded_tmtn(data):
        """Handle file uploads for TMNT functionality via SocketIO."""
        try:
            filename = data['filename']
            file_content = data['data']  # Assume this is already in bytes
            
            # Convert the file data back to a file-like object (for processing)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], secure_filename(filename))
            
            # Ensure the upload folder exists before writing
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save the uploaded file data to disk (using binary mode)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Notify client of processing status
            emit('processing_status_tmtn', {'status': 'processing', 'message': 'Processing the file...'})

            # Process the file
            result = calculate_total_qty(file_path)

            # Check if the result is an error message or a tuple of file paths
            if isinstance(result, tuple):
                warehouse_file_path, kitchen_file_path = result

                # Create a zip file containing both Excel files
                zip_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'output_files.zip')
                os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)  # Ensure directory exists
                with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                    zipf.write(warehouse_file_path, os.path.basename(warehouse_file_path))
                    zipf.write(kitchen_file_path, os.path.basename(kitchen_file_path))

                # Emit success message and provide the download link
                emit('processing_status_tmtn', {
                    'status': 'success',
                    'message': 'Files processed successfully!',
                    'file_url': url_for('download_file', filename='output_files.zip', _external=True)
                })
            else:
                # Emit error message
                emit('processing_status_tmtn', {
                    'status': 'error',
                    'message': result  # This is the error message string from calculate_total_qty
                })
        except Exception as e:
            # Emit a generic error message in case of unexpected errors
            print(f"Error processing file_uploaded_tmtn: {e}")  # Log the error for debugging
            emit('processing_status_tmtn', {
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            })
