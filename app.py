from flask import Flask, render_template_string
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders")
    
    # Fetch all rows from the executed query
    rows = cursor.fetchall()
    
    # Close the database connection
    conn.close()
    
    # HTML template to render
    html = """
    <html>
    <head><title>Orders</title></head>
    <body>
    <h1>Orders</h1>
    <table border="1">
    <tr>
        <th>ID</th>
        <th>Order ID</th>
        <th>Verification ID</th>
        <th>GIA Floor</th>
    </tr>
    {% for row in rows %}
    <tr>
        <td>{{ row[0] }}</td>
        <td>{{ row[1] }}</td>
        <td>{{ row[2] }}</td>
        <td>{{ row[3] }}</td>
    </tr>
    {% endfor %}
    </table>
    </body>
    </html>
    """
    
    return render_template_string(html, rows=rows)

if __name__ == '__main__':
    app.run(debug=True)
