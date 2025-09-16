from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return render_template('index.html', orders=orders)

@app.route('/searchById', methods=['GET'])
def search1():
    query = request.args.get('query1')
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE verification_id LIKE ?', ('%' + query + '%',)).fetchall()
    conn.close()
    return render_template('index.html', orders=orders)

@app.route('/searchByPN', methods=['GET'])
def search2():
    query = request.args.get('query2')
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE phone_number LIKE ?', ('%' + query + '%',)).fetchall()
    conn.close()
    return render_template('index.html', orders=orders)

@app.route('/update-status', methods=['POST'])
def update_status():
    data = request.get_json()
    id = data.get('id')
    conn = get_db_connection()
    with conn:
        conn.execute("UPDATE orders SET status = 'Arrived at GIA' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': 'success'})


if __name__ == '__main__':
    app.run(debug=True)
