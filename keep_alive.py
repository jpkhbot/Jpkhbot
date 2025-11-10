from flask import Flask
from threading import Thread
import logging

logging.getLogger('werkzeug').setLevel(logging.WARNING)

app = Flask('')

@app.route('/')
def home():
    return """
    <html>
        <head><title>Discogs Bot</title></head>
        <body>
            <h1>🎵 Discogs Wantlist Bot</h1>
            <p>✅ Bot is active and monitoring your wantlist!</p>
        </body>
    </html>
    """

def run():
    app.run(host='0.0.0.0', port=3000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
