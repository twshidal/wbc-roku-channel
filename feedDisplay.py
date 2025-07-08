from flask import Flask, render_template, jsonify
import subprocess
import sys
import logging
import json
import os

# Constants
JSON_FILE = "WorthBC.json"
FEED_CAPTURE_SCRIPT = "feedCapture.py"

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)


@app.route('/run-script')
def run_script():
    try:
        result = subprocess.run(
            [sys.executable, FEED_CAPTURE_SCRIPT],
            check=True,
            capture_output=True,
            text=True
        )
        logging.info("Script executed successfully")
        return jsonify({"message": "Script executed successfully", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        error_message = e.stderr if e.stderr else str(e)
        logging.error(f"An error occurred: {error_message}")
        return jsonify({"error": "An error occurred while running the script", "details": error_message}), 500


@app.route('/')
def index():
    if not os.path.exists(JSON_FILE):
        logging.error(f"{JSON_FILE} does not exist.")
        return "Feed file not found.", 500

    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    channel_info = data.get("channel_info", {})
    movies = data.get("movies", [])

    return render_template('index.html', channel_info=channel_info, movies=movies)


if __name__ == "__main__":
    app.run(debug=True)
