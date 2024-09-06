import os
from flask import current_app, request, send_file, render_template, url_for, jsonify
from werkzeug.utils import secure_filename
import zipfile
from .tmtn import allowed_file, calculate_total_qty
from .totc import extract_and_calculate_usage
from .matcher import daily_matcher
import logging

# Initialize logging
logger = logging.getLogger(__name__)

def register_routes(app):
    @app.route('/test_download/<filename>')
    def test_download(filename):
        file_path = os.path.join('/home/accountant/mysite/calma_acc/uploads', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "File not found", 404
    # Home Page Route
    @app.route('/')
    def main_page():
        return render_template('main.html')

    # Transfer Material to Needed Route
    @app.route('/transfer_material_to_needed', methods=['GET', 'POST'])
    def transfer_material_to_needed():
        return render_template('transfer_material_to_needed.html')

    # Transfer Orders to Components Route
    @app.route('/transfer_orders_to_components', methods=['GET', 'POST'])
    def transfer_orders_to_components():
        return render_template('transfer_orders_to_components.html')

    # Daily Matcher Route
    @app.route('/daily_matcher_page', methods=['GET', 'POST'])
    def daily_matcher_page():
        return render_template('daily_matcher.html')

    # Download File Route
    @app.route('/download/<filename>')
    def download_file(filename):
        """Allow users to download processed files."""
        try:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            logger.info(f"Trying to download: {file_path}")
            if os.path.exists(file_path):
                logger.info(f"File found: {file_path}")
                return send_file(file_path, as_attachment=True)
            else:
                logger.error(f"File not found: {file_path}")
                return "File not found", 404
        except Exception as e:
            logger.error(f"Error while downloading file: {e}")
            return jsonify({'status': 'error', 'message': f'Error downloading file: {e}'}), 500


    # Upload and Process TMNT File Route
    @app.route('/upload_file_tmtn', methods=['POST'])
    def upload_file_tmtn():
        """Handle file uploads for TMNT functionality."""
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part in the request'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400

        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)

                result = calculate_total_qty(file_path)

                if isinstance(result, tuple):
                    warehouse_file_path, kitchen_file_path = result
                    zip_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'output_files.zip')
                    os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)

                    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                        zipf.write(warehouse_file_path, os.path.basename(warehouse_file_path))
                        zipf.write(kitchen_file_path, os.path.basename(kitchen_file_path))

                    return jsonify({
                        'status': 'success',
                        'message': 'Files processed successfully!',
                        'file_url': url_for('download_file', filename='output_files.zip', _external=True)
                    })
                else:
                    logger.error(f"Error in TMNT processing: {result}")
                    return jsonify({'status': 'error', 'message': result}), 400

            except Exception as e:
                logger.error(f"Error processing TMNT file: {e}")
                return jsonify({'status': 'error', 'message': f'An error occurred: {str(e)}'}), 500
        else:
            return jsonify({'status': 'error', 'message': 'Invalid file format'}), 400

    # Upload and Process Matcher File Route
    @app.route('/upload_file_matcher', methods=['POST'])
    def upload_file_matcher():
        """Handle file uploads for Matcher functionality."""
        try:
            if 'file' not in request.files:
                return jsonify({'status': 'error', 'message': 'No file part in the request'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'status': 'error', 'message': 'No file selected'}), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path1 = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                os.makedirs(os.path.dirname(file_path1), exist_ok=True)
                file.save(file_path1)

                processed_file_path = daily_matcher(file_path1)

                if processed_file_path.startswith('An error occurred'):
                    logger.error(f"Error in Matcher processing: {processed_file_path}")
                    return jsonify({'status': 'error', 'message': 'Error processing the file.'}), 500
                else:
                    return jsonify({
                        'status': 'success',
                        'message': 'File processed successfully!',
                        'file_url': url_for('download_file', filename='final_matcher.xlsx', _external=True)
                    })
            else:
                return jsonify({'status': 'error', 'message': 'Invalid file format'}), 400
        except Exception as e:
            logger.error(f"Error processing Matcher file: {e}")
            return jsonify({'status': 'error', 'message': f'An error occurred: {str(e)}'}), 500

    # Upload and Process TOTC File Route
    @app.route('/upload_file_totc', methods=['POST'])
    def upload_file_totc():
        """Handle file uploads for TOTC functionality."""
        try:
            if 'file' not in request.files:
                return jsonify({'status': 'error', 'message': 'No file part in the request'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'status': 'error', 'message': 'No file selected'}), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path1 = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

                os.makedirs(os.path.dirname(file_path1), exist_ok=True)
                file.save(file_path1)

                processed_file_path = extract_and_calculate_usage(file_path1)

                if processed_file_path.startswith('An error occurred'):
                    logger.error(f"Error in TOTC processing: {processed_file_path}")
                    return jsonify({'status': 'error', 'message': 'Error processing the file.'}), 500
                else:
                    return jsonify({
                        'status': 'success',
                        'message': 'File processed successfully!',
                        'file_url': url_for('download_file', filename='final_content_usage.xlsx', _external=True)
                    })
            else:
                return jsonify({'status': 'error', 'message': 'Invalid file format'}), 400
        except Exception as e:
            logger.error(f"Error processing TOTC file: {e}")
            return jsonify({'status': 'error', 'message': f'An error occurred: {str(e)}'}), 500
