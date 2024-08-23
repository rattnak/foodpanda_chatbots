from flask import Flask, render_template_string, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Fetch existing data from `orders` table
    cursor.execute("SELECT * FROM orders")
    rows = cursor.fetchall()
    
    # Fetch only entries from `received_orders` that exist
    cursor.execute("SELECT * FROM received_orders")
    received_orders = cursor.fetchall()
    
    conn.close()


    html = """
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Customer Orders Dashboard</title>
            <style>
                *{
                    border-radius: 5px;
                }
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                }
                h1 {
                    text-align: center;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }
                th, td {
                    padding: 10px;
                    text-align: left;
                    border: 1px solid #ddd;
                }
                th {
                    background-color: #f4f4f4;
                }
                .dashboard {
                    display: flex;
                    justify-content: space-between;
                }
                .box {
                    width: 48%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    background-color: #f9f9f9;
                }
                .order-select {
                    width: 100%;
                    padding: 5px;
                    margin-bottom: 10px;
                }
                .deliver-button {
                    padding: 5px 10px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
                .deliver-button:hover {
                    background-color: #45a049;
                }
                .on-way-button {
                    background-color: #007bff;
                }
                .on-way-button:hover {
                    background-color: #0056b3;
                }
            </style>
        </head>
        <body>

        <h1>Customer Orders Dashboard</h1>

        <div class="dashboard">
            <!-- Recent Orders Section -->
            <div class="box">
                <h2>Recent Orders</h2>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Order ID</th>
                        <th>Verification ID</th>
                        <th>GIA Floor</th>
                        <th>Received</th>
                    </tr>
                    {% for row in rows %}
                    <tr>
                        <td>{{ row[0] }}</td>
                        <td>{{ row[1] }}</td>
                        <td>{{ row[2] }}</td>
                        <td>{{ row[3] }}</td>
                        <td>
                            <select class="order-select" onchange="markAsReceived('{{ row[2] }}', {{ row[3] }}, {{ row[0] }}, this.value)">
                                <option value="no">No</option>
                                <option value="yes">Yes</option>
                            </select>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>

            <!-- Received Orders Section -->
            <div class="box">
                <h2>Received Orders by Floor</h2>
                <table id="received-orders-table">
                    <tr>
                        <th>Floor</th>
                        <th>Verification IDs</th>
                        <th>Actions</th>
                    </tr>
                    {% for order in received_orders %}
                    <tr id="floor-{{ order[2] }}">
                        <td rowspan="1">Floor {{ order[2] }}</td>
                        <td>
                            {{ order[1] }}
                        </td>
                        <td>
                            <button class="on-way-button" onclick="onWay('{{ order[2] }}')">On the Way</button>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>

        <!-- JavaScript to handle interactions -->
        <script>
            function markAsReceived(verificationId, floor, orderId, status) {
                fetch('/update_received_order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        verification_id: verificationId,
                        floor: floor,
                        order_id: orderId,
                        status: status
                    }),
                })
                .then(response => response.json())
                .then(data => {
                    const table = document.getElementById('received-orders-table');
                    let floorRow = document.querySelector(`#floor-${floor}`);

                    if (status === "yes") {
                        if (!floorRow) {
                            floorRow = document.createElement('tr');
                            floorRow.id = `floor-${floor}`;
                            floorRow.innerHTML = `
                                <td rowspan="1">Floor ${floor}</td>
                                <td>
                                    ${verificationId}
                                </td>
                                <td>
                                    <button class="on-way-button" onclick="onWay('${floor}')">On the Way</button>
                                </td>
                            `;
                            table.appendChild(floorRow);
                        } else {
                            const verificationCell = floorRow.querySelector('td:nth-child(2)');
                            verificationCell.innerHTML += `<br>${verificationId}`;
                        }
                    } else if (status === "no") {
                        if (floorRow) {
                            const verificationCell = floorRow.querySelector('td:nth-child(2)');
                            const verificationIds = verificationCell.innerHTML.split('<br>');
                            const updatedVerificationIds = verificationIds.filter(id => id !== verificationId);

                            if (updatedVerificationIds.length > 0) {
                                verificationCell.innerHTML = updatedVerificationIds.join('<br>');
                            } else {
                                table.removeChild(floorRow);
                            }
                        }
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            }

            function onWay(floor) {
                alert(`Orders for Floor ${floor} are now on the way!`);
            }
        </script>

        </body>
    </html>
    """

    return render_template_string(html, rows=rows, received_orders=received_orders)

@app.route('/update_received_order', methods=['POST'])
def update_received_order():
    data = request.json
    verification_id = data.get('verification_id')
    floor = data.get('floor')
    status = data.get('status')

    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # Update the status in the orders table
        cursor.execute(
            "UPDATE orders SET status = ? WHERE verification_id = ? AND gia_floor = ?",
            (status, verification_id, floor)
        )
        
        if status == "yes":
            # Insert into received_orders if not already present
            cursor.execute(
                "SELECT COUNT(*) FROM received_orders WHERE verification_id = ? AND gia_floor = ?",
                (verification_id, floor)
            )
            exists = cursor.fetchone()[0]

            if exists == 0:
                cursor.execute(
                    "INSERT INTO received_orders (verification_id, gia_floor) VALUES (?, ?)",
                    (verification_id, floor)
                )
                conn.commit()

        elif status == "no":
            # Remove from received_orders
            cursor.execute(
                "DELETE FROM received_orders WHERE verification_id = ? AND gia_floor = ?",
                (verification_id, floor)
            )
            conn.commit()

    except sqlite3.Error as e:
        return jsonify({"success": False, "error": str(e)})
    finally:
        conn.close()

    return jsonify({"success": True})



if __name__ == '__main__':
    app.run(debug=True)
