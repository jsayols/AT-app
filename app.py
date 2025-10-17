from flask import Flask, request, jsonify
import base64
from lara_sdk import Translator, Credentials
import os

app = Flask(__name__)

# Get Lara credentials from environment variables
credentials = Credentials(
    access_key_id=os.environ.get("LARA_ACCESS_KEY_ID"),
    access_key_secret=os.environ.get("LARA_ACCESS_KEY_SECRET")
)
lara = Translator(credentials)

@app.route("/translate_document", methods=["POST"])
def translate_document():
    data = request.get_json()
    filename = data.get("filename", "document.txt")
    file_b64 = data.get("file_base64")
    source = data.get("source")
    target = data.get("target")
    style = data.get("style", "neutral")
    adapt_to = data.get("adapt_to")
    glossaries = data.get("glossaries")

    if not file_b64 or not source or not target:
        return jsonify({"error": "Missing required fields"}), 400

    # Decode incoming file
    file_bytes = base64.b64decode(file_b64)
    tmp_path = f"/tmp/{filename}"
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)

    # Translate document
    translated_bytes = lara.documents.translate(
        tmp_path,
        filename,
        source=source,
        target=target,
        style=style,
        adapt_to=adapt_to,
        glossaries=glossaries
    )

    # Return base64-encoded translated file
    translated_b64 = base64.b64encode(translated_bytes).decode("utf-8")

    return jsonify({
        "filename": f"translated_{filename}",
        "file_base64": translated_b64,
        "source": source,
        "target": target,
        "style": style
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
