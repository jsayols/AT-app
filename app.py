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
    try:
        data = request.get_json()

        # Required fields
        file_b64 = data.get("file_base64")
        source = data.get("source")
        target = data.get("target")
        if not file_b64 or not source or not target:
            return jsonify({"error": "Missing required fields: file_base64, source, or target"}), 400

        # Optional fields
        filename = data.get("filename") or "document.txt"
        filename = os.path.basename(filename)  # sanitize filename
        style = data.get("style") or "neutral"
        adapt_to = data.get("adapt_to") or []
        glossaries = data.get("glossaries") or []

        # Decode Base64
        try:
            file_bytes = base64.b64decode(file_b64)
        except Exception as e:
            return jsonify({"error": f"Invalid Base64 content: {str(e)}"}), 400

        # Save temporary file
        tmp_path = os.path.join("/tmp", filename)
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

    except Exception as e:
        # Catch-all to prevent HTTP 500
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
