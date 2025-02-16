import uuid
import math
from decimal import Decimal, InvalidOperation

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# In-memory store for receipts
receipts = {}


def calculate_points(receipt):
    points = 0

    # Rule 1: One point for every alphanumeric character in the retailer name.
    retailer = receipt.get("retailer", "")
    points += sum(1 for char in retailer if char.isalnum())

    try:
        total = Decimal(receipt.get("total", "0"))
    except InvalidOperation:
        total = Decimal("0")

    # Rule 2: 50 points if the total is a round dollar amount with no cents.
    if total == total.to_integral_value():
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25.
    if (total * 100) % 25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt.
    items = receipt.get("items", [])
    points += (len(items) // 2) * 5

    # Rule 5: For each item, if the trimmed description’s length is a multiple of 3,
    # multiply the price by 0.2 and round up to the nearest integer.
    for item in items:
        description = item.get("shortDescription", "").strip()
        if len(description) % 3 == 0:
            try:
                price = Decimal(item.get("price", "0"))
            except InvalidOperation:
                price = Decimal("0")
            bonus = math.ceil(price * Decimal("0.2"))
            points += bonus

    # Rule 6: 6 points if the day in the purchase date is odd.
    purchase_date = receipt.get("purchaseDate", "")
    try:
        date_obj = datetime.strptime(purchase_date, "%Y-%m-%d")
        if date_obj.day % 2 == 1:
            points += 6
    except ValueError:
        # If the date is not in the expected format, ignore this rule.
        pass

    # Rule 7: 10 points if the time of purchase is between 2:00pm and 4:00pm.
    purchase_time = receipt.get("purchaseTime", "")
    try:
        time_obj = datetime.strptime(purchase_time, "%H:%M")
        if 14 <= time_obj.hour < 16:
            points += 10
    except ValueError:
        # If the time is not in the expected format, ignore this rule.
        pass

    return points


@app.route("/receipts/process", methods=["POST"])
def process_receipt():
    if not request.is_json:
        return jsonify({"error": "Request payload must be in JSON format"}), 400

    receipt = request.get_json()
    # You might want to add more validation for required fields here.

    receipt_id = str(uuid.uuid4())
    receipts[receipt_id] = receipt
    return jsonify({"id": receipt_id}), 200


@app.route("/receipts/<receipt_id>/points", methods=["GET"])
def get_points(receipt_id):
    receipt = receipts.get(receipt_id)
    if receipt is None:
        return jsonify({"error": "Receipt not found"}), 404

    points = calculate_points(receipt)
    return jsonify({"points": points}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
