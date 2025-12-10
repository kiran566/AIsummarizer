from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDF reading

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])



@app.get("/")
def home():
    return render_template("index.html")


@app.get("/text")
def text_page():
    return render_template("text.html")


@app.get("/pdf")
def pdf_page():
    return render_template("pdf.html")



#UMMARY FUNCTION 
def get_summary(prompt):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"Summarize the following text clearly and concisely:\n{prompt}"
    )
    return response.output_text.strip()


#TEXT
@app.route("/summarize/text", methods=["POST"])
def summarize_text():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    summary = get_summary(text)
    return jsonify({"summary": summary})


#  PDF SUMMARY 
@app.route("/summarize/pdf", methods=["POST"])
def summarize_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "File is not a PDF"}), 400

    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""

    for page in doc:
        text += page.get_text()

    summary = get_summary(text)
    return jsonify({"summary": summary})


# RUN FLASK 
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
