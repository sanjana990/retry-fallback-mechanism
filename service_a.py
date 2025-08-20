from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route("/data")
def get_data():
    if random.random() < 0.6:  # 60% chance to fail
        return "Service A failed", 500
    return jsonify({"source": "Service A", "data": "Hello from A!"})

if __name__ == "__main__":
    app.run(port=5001)
