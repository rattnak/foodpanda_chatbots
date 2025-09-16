import sqlite3
import csv

def export_to_csv(db_name, table_name, output_csv):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query to select all data from the specified table
    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)

    # Fetch all rows from the table
    rows = cursor.fetchall()

    # Get column names from the table
    column_names = [description[0] for description in cursor.description]

    # Write data to a CSV file
    with open(output_csv, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(column_names)  # Write column headers
        writer.writerows(rows)         # Write data rows

    # Close the database connection
    conn.close()

    print(f"Data from table '{table_name}' has been exported to '{output_csv}'")

# Example usage
db_name = 'database.db'    
table_name = 'orders' 
output_csv = 'FloorExpress.csv'        

export_to_csv(db_name, table_name, output_csv)
