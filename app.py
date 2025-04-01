import os
import pandas as pd
from flask import Flask, request, jsonify, send_file, render_template
import threading
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
OUTPUT_FILE = r"D:\Excelmate AI\output.xlsx"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ✅ Import 'extraction.py' safely
try:
    from extraction import extract_and_save
    print("Module 'extraction' imported successfully!")
except ImportError as e:
    print("Error importing 'extraction':", e)

# ✅ Route for HTML Home Page
@app.route("/")
def index():
    return render_template("index.html")

# ✅ Route for File Upload and Processing
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    try:
        # Run extraction in a separate thread (Daemon mode)
        thread = threading.Thread(target=extract_and_save, args=(file_path, OUTPUT_FILE), daemon=True)
        thread.start()
        print(f"Processing started for {filename} in a separate thread.")
    except Exception as e:
        print("Error in starting extraction thread:", e)
        return jsonify({"error": "Failed to start processing"}), 500

    return jsonify({"message": "File uploaded successfully. Processing started."}), 200

# ✅ Route to Download Processed Excel File
@app.route("/download", methods=["GET"])
def download_file():
    if not os.path.exists(OUTPUT_FILE):
        return jsonify({"error": "No processed file found"}), 404

    return send_file(OUTPUT_FILE, as_attachment=True)

# ✅ Route to Get Processed Data (for Dash)
@app.route("/get_data", methods=["GET"])
def get_data():
    if not os.path.exists(OUTPUT_FILE):
        return jsonify({"error": "No processed data found"}), 404

    try:
        df = pd.read_excel(OUTPUT_FILE, engine="openpyxl")
        return df.to_json(orient="records")
    except Exception as e:
        print("Error reading Excel file:", e)
        return jsonify({"error": "Failed to read processed data"}), 500

if __name__ == "__main__":
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print("Error starting Flask app:", e)
