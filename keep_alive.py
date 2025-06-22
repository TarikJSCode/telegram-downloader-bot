from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!", 200

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port))
    thread.start()
