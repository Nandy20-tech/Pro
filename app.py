import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask is running on Render!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Change default 10000 to 8080
    app.run(host='0.0.0.0', port=port)
