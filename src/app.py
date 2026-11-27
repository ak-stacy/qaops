import math
import os

from flask import Flask, jsonify, request

from utils.math import add

app = Flask(__name__)


@app.get("/healthz")
def health():
    return jsonify(status="ok", environment=os.getenv("QAOPS_ENV", "local"))


@app.post("/api/sum")
def sum_values():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Request body must be a JSON object"), 400

    left = payload.get("a")
    right = payload.get("b")
    values = (left, right)
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        for value in values
    ):
        return jsonify(error="Fields 'a' and 'b' must be finite numbers"), 400

    return jsonify(result=add(left, right))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
    )
