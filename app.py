from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
import cv2
import os

app = Flask(__name__)
CORS(app)

# 👉 Set Tesseract path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files.get('file')

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        print("📂 File received:", file.filename)

        # 🧠 Read image
        img = cv2.imread(filepath)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 📄 OCR
        text = pytesseract.image_to_string(gray)
        print("📄 Extracted Text:\n", text)

        # 🔥 STEP: Extract form fields dynamically
        lines = text.split("\n")
        fields = []

        for line in lines:
            line = line.strip()

            # detect field labels like "Name:", "DOB:", etc.
            if ":" in line:
                field = line.split(":")[0].strip().lower()
                field = field.replace(" ", "_")
                fields.append(field)

        # remove duplicates
        fields = list(set(fields))

        # 🧾 Create dynamic JSON
        data = {}
        for field in fields:
            data[field] = ""

        print("🧾 Dynamic JSON:", data)

        return jsonify({
            "extracted_text": text,
            "structured_data": data
        })

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)