import sys
import sqlite3
import time
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QInputDialog
from flask import Flask, request, jsonify

# Flask Server Setup
app = Flask(__name__)

# Database Initialization
def init_db():
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        name TEXT PRIMARY KEY,
        quantity INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/transform", methods=["POST"])
def transform():
    time.sleep(10)
    data = request.json
    print("Received Transform Data:", data)
    return jsonify({"message": "Transform received"}), 200

@app.route("/file-path", methods=["GET"])
def file_path():
    project_path = request.args.get("projectpath", False)
    return jsonify({"path": "C:/Projects/MyDCCFile.blend" if not project_path else "C:/Projects"}), 200

@app.route("/add-item", methods=["POST"])
def add_item():
    time.sleep(10)
    data = request.json
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO inventory (name, quantity) VALUES (?, ?) ON CONFLICT(name) DO UPDATE SET quantity = quantity + ?", (data["name"], data["quantity"], data["quantity"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Item added"}), 200

@app.route("/remove-item", methods=["POST"])
def remove_item():
    time.sleep(10)
    data = request.json
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ?", (data["name"],))
    conn.commit()
    conn.close()
    return jsonify({"message": "Item removed"}), 200

# PyQt UI
class InventoryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.listWidget = QListWidget()
        self.refreshButton = QPushButton("Refresh Inventory")
        self.addButton = QPushButton("Add Item")
        self.removeButton = QPushButton("Remove Item")

        self.layout.addWidget(QLabel("Inventory"))
        self.layout.addWidget(self.listWidget)
        self.layout.addWidget(self.refreshButton)
        self.layout.addWidget(self.addButton)
        self.layout.addWidget(self.removeButton)
        
        self.refreshButton.clicked.connect(self.load_inventory)
        self.addButton.clicked.connect(self.add_item)
        self.removeButton.clicked.connect(self.remove_item)
        
        self.setLayout(self.layout)
        self.load_inventory()

    def load_inventory(self):
        self.listWidget.clear()
        conn = sqlite3.connect("inventory.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        for row in cursor.fetchall():
            self.listWidget.addItem(f"{row[0]}: {row[1]}")
        conn.close()

    def add_item(self):
        name, ok = QInputDialog.getText(self, "Add Item", "Enter item name:")
        if ok:
            quantity, ok = QInputDialog.getInt(self, "Add Item", "Enter quantity:")
            if ok:
                requests.post("http://127.0.0.1:5000/add-item", json={"name": name, "quantity": quantity})
                self.load_inventory()

    def remove_item(self):
        selected = self.listWidget.currentItem()
        if selected:
            name = selected.text().split(":")[0]
            requests.post("http://127.0.0.1:5000/remove-item", json={"name": name})
            self.load_inventory()

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(debug=True, use_reloader=False)).start()
    
    app = QApplication(sys.argv)
    ex = InventoryApp()
    ex.show()
    sys.exit(app.exec_())
