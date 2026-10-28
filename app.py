from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from checker import analyze_document
import os

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED = {"pdf", "docx", "txt"}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        f = request.files.get("file")

        if not f or not f.filename:
            error = "Please select a PDF, DOCX, or TXT file."
        else:
            ext = f.filename.rsplit(".", 1)[-1].lower()

            if ext not in ALLOWED:
                error = "Only PDF, DOCX and TXT files are supported."
            else:
                name = secure_filename(f.filename)
                path = os.path.join(UPLOAD_DIR, name)
                f.save(path)

                try:
                    result = analyze_document(path)
                except Exception as e:
                    error = f"Analysis failed: {e}"

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)
