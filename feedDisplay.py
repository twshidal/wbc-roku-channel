from flask import Flask, render_template, jsonify
import subprocess
import sys
import logging
import json

# Constant variables
JSON_FILE = "WorthBC.json"
FEED_CAPTURE_SCRIPT = "feedCapture.py"

app = Flask(__name__)


# Configure logging
logging.basicConfig(level=logging.INFO)


# Route to run the external script
@app.route('/run-script')
def run_script():
    try:
        # Execute the external script using the same Python interpreter
        result = subprocess.run([sys.executable, FEED_CAPTURE_SCRIPT], check=True, capture_output=True, text=True)
        logging.info("Script executed successfully")
        return jsonify({"message": "Script executed successfully", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        # Capture and display the error output for debugging
        error_message = e.stderr if e.stderr else str(e)
        logging.error(f"An error occurred while running the script: {error_message}")
        return jsonify({"error": "An error occurred while running the script", "details": error_message}), 500


@app.route('/')
def index():
    # Read the JSON file
    with open(JSON_FILE) as json_file:
        data = json.load(json_file)  # Parse JSON file into a Python dictionary

    # Verify that items is actually a list
    if isinstance(data.get('items'), list):
        print("Data items is a list, proceeding to render...")
    else:
        print("Error: Data items is not a list.")

    return render_template('index.html', data=data)


if __name__ == "__main__":
    app.run(debug=True)
