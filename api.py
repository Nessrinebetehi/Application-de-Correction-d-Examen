from flask import Flask, request, jsonify

app = Flask(__name__)

# بيانات تجريبية
data = [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"}
]

# المسار الأساسي
@app.route("/")
def home():
    return "Flask API is running!"

# الحصول على جميع العناصر
@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(data)

# الحصول على عنصر معين عبر الـ ID
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = next((item for item in data if item["id"] == item_id), None)
    if item:
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

# إضافة عنصر جديد
@app.route("/items", methods=["POST"])
def add_item():
    new_item = request.json
    if "id" not in new_item or "name" not in new_item:
        return jsonify({"error": "Invalid data"}), 400

    data.append(new_item)
    return jsonify(new_item), 201

# تشغيل التطبيق
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
