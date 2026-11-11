import os
from flask import Flask, jsonify, render_template

app = Flask(__name__)
VERSION = os.getenv("APP_VERSION", "v1")
COLOR = os.getenv("APP_COLOR", "blue")  # blue or green release (used in blue-green activity)


@app.route("/")
def index():
    return render_template("index.html", version=VERSION, color=COLOR)


@app.route("/health")
def health():
    return jsonify(status="ok", version=VERSION, color=COLOR)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
