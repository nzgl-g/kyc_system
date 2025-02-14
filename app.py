from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import json
from decision_engine import run_pipeline, kyc_decision  # Import your existing pipeline

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create uploads folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/verify_kyc', methods=['POST'])
def verify_kyc():
    try:
        # Check if image file is present
        if 'id_image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['id_image']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            # Create unique filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Prepare form data
            form_data = {
                'full_name': request.form.get('full_name'),
                'dob': request.form.get('dob'),
                'nationality': request.form.get('nationality'),
                'id_number': request.form.get('id_number')
            }

            # Run KYC pipeline
            pipeline_results = run_pipeline(form_data, filepath)

            # Get final decision
            decision = kyc_decision(pipeline_results)

            # Clean up uploaded file
            os.remove(filepath)

            # Try to parse the decision as JSON
            try:
                decision_json = json.loads(decision)
            except:
                # If it's not valid JSON, create a structured response
                decision_json = {
                    "status": "KYC Worked peacefully",
                    "message": decision
                }

            return jsonify({
                'status': 'success',
                'pipeline_results': pipeline_results,
                'decision': json.dumps(decision_json)
            })

        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)