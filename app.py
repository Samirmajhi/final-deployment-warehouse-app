import base64
from flask import Flask, render_template,redirect, url_for, request, send_from_directory, send_file, jsonify,flash
from flask import Flask, request, render_template_string
from flask_cors import CORS
from flask import g
import os
import threading
import cv2 
import numpy as np
from pyzbar.pyzbar import decode 
import time
import mysql.connector 
from flask import Flask, request, jsonify, redirect,send_from_directory,session

import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__,static_url_path='/static')

CORS(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db_connection = mysql.connector.connect(
    host="10.38.176.3",
    user="fishtail_123",
    password='#fishtail@This7',
    port = 3306,
    database="fishtail_user"
)
cursor = db_connection.cursor()



from flask import g

# Function to get the database connection
def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host="10.38.176.3",
            user="fishtail_123",
            password='#fishtail@This7',
            port=3306,
            database="fishtail_user"
        )
    return g.db
def get_cursor():
    if 'cursor' not in g:
        g.cursor = get_db().cursor()
    return g.cursor

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

selected_status = None

# @app.route('/',methods=['GET'])
# def index():
#     return send_from_directory('static', 'fiishtail_warehouse.html')



@app.route('/')
def index():
    return render_template('fishtail2.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        cursor = db_connection.cursor()
        first_name = request.form['FirstName']
        last_name = request.form['LastName']
        email = request.form['Email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        errors = []
        if not first_name or not last_name or not email or not password or not confirm_password:
            errors.append("Please fill in all required fields")
        else:
            if '@' not in email or '.' not in email:
                errors.append("Email Format is Invalid!")
            if len(password) < 8 or not any(char.isupper() for char in password) or not any(char in '!@#$%^&*()-=+{};:,<.>/' for char in password):
                errors.append("Password should be 8 characters long, contain at least one uppercase letter, and one special character!")
            if password != confirm_password:
                errors.append("Passwords do not match")
        
        if not errors:
            sql_check_email = "SELECT email FROM users WHERE email=%s"
            cursor.execute(sql_check_email, (email,))
            if cursor.fetchone():
                errors.append("Email already exists. Please use a different email address.")
        
        if not errors:
            hashed_password = generate_password_hash(password)
            sql = "INSERT INTO users (FirstName, LastName, email, password) VALUES (%s, %s, %s, %s)"
            try:
                cursor.execute(sql, (first_name, last_name, email, hashed_password))
                db_connection.commit()
                flash('Sign up successful! Redirecting to warehouse page...')
                return redirect(url_for('index'))
            except mysql.connector.IntegrityError:
                errors.append("An Error Occurred while signing you up")

        return render_template('Fishtail.html', errors=errors)
    
    # If the request method is GET, render the signup form without errors
    return render_template('Fishtail.html', errors=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return  redirect(url_for('fiishtail_warehouse'))
    if request.method == 'POST':
        cursor = db_connection.cursor()
        email = request.form['Email']
        password = request.form['Password']
        errors = []
        sql = "SELECT password FROM users WHERE email=%s"
        cursor.execute(sql, (email,))
        result = cursor.fetchone()
        if result:
            stored_password = result[0]
            if check_password_hash(stored_password, password):
                session['logged_in'] = True
                flash("Successfully Logged in. Redirecting to the main page.")
                return redirect(url_for('fiishtail_warehouse'))
            else:
                errors.append("Password doesn't match")
        else:
            errors.append("User not found")
        return render_template('fishtail2.html', errors=errors)
    return render_template('fishtail2.html', errors=[])

@app.route('/fiishtail_warehouse')
def fiishtail_warehouse():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('fiishtail_warehouse.html')

@app.route('/logout')
def logout():   
    session.pop('logged_in', None)
    # Clear flash messages
    session.pop('_flashes', None)
    response = redirect(url_for('login'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/barcodes')
def barcodes():
    return render_template('barcodes.html')

@app.route('/see_table')
def see_table():
    return render_template('see_table.html')

@app.route('/search')
def search():
    return render_template('search.html')

from flask import jsonify

import logging

# Define a logger
logger = logging.getLogger('product_logger')
logger.setLevel(logging.ERROR)

# Define a file handler
file_handler = logging.FileHandler('product_error.log')
file_handler.setLevel(logging.ERROR)

# Define a formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

@app.route('/add_product', methods=['POST'])
def add_product():
    db_connection = mysql.connector.connect(
    host="10.38.176.3",
    user="fishtail_123",
    password='#fishtail@This7',
    port = 3306,
    database="fishtail_user"
)

    cursor = db_connection.cursor()
    data = request.get_json()
    EAN_13 = data.get('ean')
    Product_Name = data.get('name')
    Product_Quantity = data.get('quantity')
    
    try:
        sql = "INSERT INTO product_detail (EAN_13, Product_Name, Product_Quantity) VALUES (%s, %s, %s)"
        cursor.execute(sql, (EAN_13, Product_Name, Product_Quantity))
        db_connection.commit()
        return jsonify({'success': True, 'message': 'Data Added Successfully'})
    except mysql.connector.Error as err:
        if err.errno == 1062:  # Duplicate entry error code
            error_message = 'The Entered EAN_13 Already Exists'
        else:
            error_message = f'Error: {err.msg}'
        logger.error(error_message)  # Log the error
        return jsonify({'success': False, 'error': error_message}), 400

@app.route('/recent_scans', methods=['GET'])
def get_recent_scans():
    try:
        db_connection = mysql.connector.connect(
    host="10.38.176.3",
    user="fishtail_123",
    password='#fishtail@This7',
    port = 3306,
    database="fishtail_user"
)

        cursor = db_connection.cursor(dictionary=True)  # Use dictionary cursor for easier data handling
        query = "SELECT EAN_13, Status FROM products_info ORDER BY timestamp DESC LIMIT 5"
        cursor.execute(query)
        recent_scans = cursor.fetchall()
        db_connection.close()
        return jsonify(recent_scans)
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db_connection' in locals():
            db_connection.close()
            
@app.route('/product_details/<ean>', methods=['GET'])
def get_product_details(ean):
    try:
        db_connection = mysql.connector.connect(
            host="10.38.176.3",
            user="fishtail_123",
            password='#fishtail@This7',
            port=3306,
            database="fishtail_user"
        )

        cursor = db_connection.cursor(dictionary=True)
        query = """
        SELECT pi.EAN_13, pi.Status, pd.Product_Name, pd.Product_Quantity
        FROM products_info pi
        JOIN product_detail pd ON pi.EAN_13 = pd.EAN_13
        WHERE pi.EAN_13 = %s
        """
        cursor.execute(query, (ean,))
        product_details = cursor.fetchone()
        db_connection.close()

        if product_details:
            return jsonify(product_details)
        else:
            return jsonify({"error": "Product not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db_connection' in locals():
            db_connection.close()
@app.route('/search', methods=['POST'])
def search_products():
    if request.method == 'POST':
        search_term = request.json.get('search', '')
        page = int(request.json.get('page', 1))
        per_page = int(request.json.get('per_page', 10))
        offset = (page - 1) * per_page
        
        if search_term:
            cursor = get_db_cursor()
            sql = """
                SELECT scan_id, EAN_13, timestamp, Status, scan_count FROM products_info 
                WHERE EAN_13 LIKE %s OR Status LIKE %s
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (f'%{search_term}%', f'%{search_term}%', per_page, offset))
            result = cursor.fetchall()
            cursor.execute("SELECT COUNT(*) FROM products_info WHERE EAN_13 LIKE %s OR Status LIKE %s", 
                           (f'%{search_term}%', f'%{search_term}%'))
            total_results = cursor.fetchone()[0]
            cursor.close()
            
            total_pages = (total_results + per_page - 1) // per_page  # Calculate total number of pages

            if result:
                response = {
                    "html": render_template_string("""
                        <table id="searchResults">
                        <thead>
                            <tr>
                            <th>Scan_Id</th>
                            <th>EAN</th>
                            <th>Timestamp</th>
                            <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in result %}
                            <tr>
                            <td>{{ row[0] }}</td>
                            <td>{{ row[1] }}</td>
                            <td>{{ row[2] }}</td>
                            <td>{{ row[3] }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                        </table>
                    """, result=result),
                    "total_pages": total_pages,
                    "current_page": page
                }
                return jsonify(response)
            else:
                return jsonify({"html": "No Results Found", "total_pages": 1, "current_page": 1})
        else:
            return jsonify({"html": "Please provide a search term", "total_pages": 1, "current_page": 1})
    else:
        return jsonify({"html": "Invalid Request", "total_pages": 1, "current_page": 1})
@app.route('/products', methods=['GET'])  
def get_products():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page

    db_connection = mysql.connector.connect(
        host="10.38.176.3",
        user="fishtail_123",
        password='#fishtail@This7',
        port=3306,
        database="fishtail_user"
    )
    cursor = db_connection.cursor(dictionary=True)
    sql = """
    SELECT 
        products_info.scan_id, 
        products_info.EAN_13, 
        product_detail.Product_Name, 
        product_detail.Product_Quantity,
        products_info.Status, 
        products_info.timestamp, 
        products_info.scan_count
    FROM 
        products_info
    LEFT JOIN 
        product_detail ON products_info.EAN_13 = product_detail.EAN_13
    LIMIT %s OFFSET %s
    """
    cursor.execute(sql, (per_page, offset))
    result = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM products_info LEFT JOIN product_detail ON products_info.EAN_13 = product_detail.EAN_13")
    total_results = cursor.fetchone()["COUNT(*)"]
    
    db_connection.close()

    total_pages = (total_results + per_page - 1) // per_page

    return jsonify({
        "products": result,
        "total_pages": total_pages,
        "current_page": page
    })

@app.route('/set_status', methods=['POST'])  
def set_status():
   global selected_status
   data = request.form
   selected_status = data['selectedStatus']
   print("Received", selected_status)
   return jsonify({'message': 'Status set succesfully'}), 200

# flask for retreiving list of inventories on that day
def get_db_cursor():
   if 'db_cursor' not in g:
      g.db_cursor = db_connection.cursor()
   return g.db_cursor
@app.teardown_appcontext
def close_db(error):
   if 'db_cursor' in g:
      g.db_cursor.close()

@app.route('/get_inventories', methods=['POST'])
def get_inventories():
    data = request.json
    timestamp = data.get('timestamp')
    status = data.get('Status')
    try:
        cursor = get_db_cursor()
        sql_query = "SELECT EAN_13, timestamp, scan_count FROM products_info WHERE DATE(timestamp) = %s AND Status = %s"
        cursor.execute(sql_query, (timestamp, status))
        inventories = cursor.fetchall()
        cursor.close()
        return jsonify({'inventories': inventories}), 200
    except mysql.connector.Error as err:
        print("Error:", err)
        return jsonify({'error': 'Failed to fetch'}), 500

@app.route('/filtered_data', methods=['GET'])
def filtered_data():
    status = request.args.get('status')
    date = request.args.get('date')
    inventories = []
    try:
        cursor = get_db_cursor()
        sql_query = "SELECT EAN_13, Status, timestamp, scan_count FROM products_info WHERE DATE(timestamp) = %s AND Status = %s"
        cursor.execute(sql_query, (date, status))
        inventories = cursor.fetchall()
        cursor.close()
        return render_template('filtered_data.html', status=status, date=date, inventories=inventories)
    except mysql.connector.Error as err:
        print("Error:", err)
        return jsonify({'error': 'Failed to fetch'}), 500
    
def fetch_barcode_data(selected_date):
    try:
        cursor = get_db_cursor()
        sql_query = "SELECT EAN_13 FROM products_info WHERE DATE(timestamp) = %s"
        cursor.execute(sql_query, (selected_date,))
        ean13_list = cursor.fetchall()
        cursor.close()
        # Convert the list of tuples into a list of strings
        ean13_list = [row[0] for row in ean13_list]
        return ean13_list
    except mysql.connector.Error as err:
        print("Error:", err)
        return None
@app.route('/barcode.html')
def barcode():
    selected_date = request.args.get('date')
    barcode_data = fetch_barcode_data(selected_date)
    if barcode_data is None:
        return render_template('barcode.html', barcode_data=[], selected_date=selected_date, error_message="Error fetching barcode data. Please try again later.")
    else:
        return render_template('barcode.html', barcode_data=barcode_data, selected_date=selected_date)

def update_product_status(ean_13, status):
   try:
      sql_query = "UPDATE products_info SET Status = %s WHERE EAN_13 = %s"
      cursor.execute(sql_query, (status, ean_13))           
      db_connection.commit()
      print("Status updated for product with EAN_13:", ean_13)
   except mysql.connector.Error as err:
      print("Errror:", err)
      db_connection.rollback()


def insert_products_info(ean_13, status, timestamp, scan_count):
    db_connection = mysql.connector.connect(
                host="10.38.176.3",
                user="fishtail_123",
                password='#fishtail@This7',
                port = 3306,
                database="fishtail_user"
            )
    try:
    

            
      cursor = db_connection.cursor() 
      
      
      
      
      ean_13_int = int(ean_13)
      sql_insert_query = "INSERT INTO  products_info (EAN_13, Status, Timestamp, Scan_Count) VALUES (%s,%s,%s,%s)"
      sql_check_existing_query = "SELECT COUNT(*) FROM products_info WHERE EAN_13 = %s AND Status = %s"

      cursor.execute(sql_check_existing_query, (ean_13_int, status))
      existing_records_count = cursor.fetchone()[0]

      if existing_records_count >0:
       sql_update_query = "UPDATE products_info SET Scan_Count = Scan_Count + %s WHERE EAN_13 = %s AND Status=%s"
       cursor.execute(sql_update_query, (scan_count, ean_13_int, status))
      else:
       cursor.execute(sql_insert_query, (ean_13_int, status, timestamp, scan_count ))  
      db_connection.commit()
      print("Record inserted/Updated Succesfully")
    except mysql.connector.Error as err:
         if err.errno == 1062:
            sql_update_query = "UPDATE products_info SET Scan_Count = Scan_Count + %s WHERE EAN_13 = %s AND Status = %s"
            cursor.execute(sql_update_query, (scan_count, ean_13_int, status))
            db_connection.commit()
            print("Existing record  updated ")
         else:
             print("Error:", err)
             db_connection.rollback()
    finally:
       cursor.close()

def update_scan_count(ean_13, status, scan_count):
   try:
      sql_update_query = "UPDATE products_info SET Scan_Count = Scan_Count + %s WHERE EAN_13 = %s AND Status=%s"
      cursor.execute(sql_update_query, (scan_count, ean_13, status))
      db_connection.commit()
      print("Updated Scan Count")
   except mysql.connector.Error as err:
      print("Error:", err)
      db_connection.rollback()
    
       
def retreive_product_info(ean_13):
   try:
 
      cursor = db_connection.cursor()
      sql_query = "SELECT * FROM products_info WHERE EAN_13 = %s"
      cursor.execute(sql_query, (ean_13,))
      result = cursor.fetchone()
      cursor.close()
      db_connection.close()
      if result:
       return result
      else:
       return None
   except mysql.connector.Error as err:
      print("Error:", err) 
      return None

import threading
run_camera_thread = True  # Flag to control the camera thread

# run_camera_thread = True  # Flag to control the camera thread



# @app.route('/execute_camera_script', methods=['POST'])
# def execute_camera_script():
#     print("Camera execution requested")
#     # selected_status = request.json.get('status')
#     if selected_status not in ['Entry', 'Exit', 'Examine']:
#         return jsonify({'error': 'Invalid status'}), 400

#     response = {'status': selected_status, 'results': []}
#     camera_thread = threading.Thread(target=handle_camera, args=(selected_status, response))
#     camera_thread.start()
#     camera_thread.join()  # Wait for the camera thread to complete
#     return jsonify(response), 200

@app.route('/process_image', methods=['POST'])
def process_image():
    data = request.json
    image_data = data['image']
    selected_status = data['status']
    
    # Decode base64 image
    image_data = image_data.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(image_array, flags=cv2.IMREAD_COLOR)
    
    response = {'status': selected_status, 'results': []}
    used_codes = set()

    try:
        db_connection = mysql.connector.connect(
            host="10.38.176.3",
            user="fishtail_123",
            password='#fishtail@This7',
            port=3306,
            database="fishtail_user"
        )
        cursor = db_connection.cursor()

        barcodes = decode(frame)
        if barcodes:
            for code in barcodes:
                decoded_data = code.data.decode('utf-8')
                if decoded_data not in used_codes:
                    print('Approved, Scanned Code:', decoded_data)
                    ean_13 = decoded_data

                    # Examine logic
                    if selected_status == 'Examine':
                        cursor.execute("""
                            SELECT 
                                products_info.scan_id, 
                                products_info.EAN_13, 
                                product_detail.Product_Name, 
                                products_info.Status, 
                                products_info.timestamp, 
                                products_info.scan_count
                            FROM 
                                products_info
                            LEFT JOIN 
                                product_detail ON products_info.EAN_13 = product_detail.EAN_13
                            WHERE
                                products_info.EAN_13 = %s
                        """, (ean_13,))
                        entries = cursor.fetchall()
                        response['results'] = [{'scan_id': entry[0], 'EAN_13': entry[1], 'Product_Name': entry[2], 'Status': entry[3], 'timestamp': str(entry[4]), 'scan_count': entry[5]} for entry in entries]
                        return jsonify(response)

                    # Check the most recent status
                    cursor.execute("SELECT Status FROM products_info WHERE EAN_13=%s ORDER BY timestamp DESC LIMIT 1", (ean_13,))
                    current_status = cursor.fetchone()

                    if selected_status == 'Entry':
                        if current_status and current_status[0] == 'Entry':
                            response['error'] = 'Cannot register Entry. Previous Entry exists without an Exit.'
                            return jsonify(response)
                    elif selected_status == 'Exit':
                        if not current_status or current_status[0] != 'Entry':
                            response['error'] = 'Cannot register Exit. No corresponding Entry found.'
                            return jsonify(response)

                    # Insert new record
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    scan_count = 1  # Example scan count
                    sql_insert_query = "INSERT INTO products_info (EAN_13, Status, Timestamp, Scan_Count) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql_insert_query, (ean_13, selected_status, timestamp, scan_count))
                    db_connection.commit()
                    print("Successfully inserted", selected_status)
                    used_codes.add(decoded_data)
                    response['results'].append({'product_id': ean_13})

                else:
                    print('Sorry, this code has been used')
                    # You might want to add some logic here to handle used codes

    except Exception as e:
        print("Error:", str(e))
        response['error'] = str(e)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db_connection' in locals():
            db_connection.close()

    return jsonify(response)


# def handle_camera(selected_status, response):
#     global run_camera_thread
#     run_camera_thread = True

#     try:
#         db_connection = mysql.connector.connect(
#             host="10.38.176.3",
#             user="fishtail_123",
#             password='#fishtail@This7',
#             port=3306,
#             database="fishtail_user"
#         )

#         cursor = db_connection.cursor()
#         cap = cv2.VideoCapture(0)
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
#         used_codes = set()

#         while run_camera_thread:
#             success, frame = cap.read()
#             if success:
#                 barcodes = decode(frame)
#                 if barcodes:
#                     for code in barcodes:
#                         decoded_data = code.data.decode('utf-8')
#                         if decoded_data not in used_codes:
#                             print('Approved, Scanned Code:', decoded_data)
#                             ean_13 = decoded_data

#                             # Examine logic
#                             if selected_status == 'Examine':
#                                 cursor.execute("""
#                                     SELECT 
#                                         products_info.scan_id, 
#                                         products_info.EAN_13, 
#                                         product_detail.Product_Name, 
#                                         products_info.Status, 
#                                         products_info.timestamp, 
#                                         products_info.scan_count
#                                     FROM 
#                                         products_info
#                                     LEFT JOIN 
#                                         product_detail ON products_info.EAN_13 = product_detail.EAN_13
#                                     WHERE
#                                         products_info.EAN_13 = %s
#                                 """, (ean_13,))
#                                 entries = cursor.fetchall()
#                                 response['results'] = [{'scan_id': entry[0], 'EAN_13': entry[1], 'Product_Name': entry[2], 'Status': entry[3], 'timestamp': entry[4], 'scan_count': entry[5]} for entry in entries]
#                                 run_camera_thread = False
#                                 return

#                             # Check the most recent status
#                             cursor.execute("SELECT Status FROM products_info WHERE EAN_13=%s ORDER BY timestamp DESC LIMIT 1", (ean_13,))
#                             current_status = cursor.fetchone()

#                             if selected_status == 'Entry':
#                                 if current_status and current_status[0] == 'Entry':
#                                     response['error'] = 'Cannot register Entry. Previous Entry exists without an Exit.'
#                                     run_camera_thread = False
#                                     return
#                             elif selected_status == 'Exit':
#                                 if not current_status or current_status[0] != 'Entry':
#                                     response['error'] = 'Cannot register Exit. No corresponding Entry found.'
#                                     run_camera_thread = False
#                                     return

#                             # Insert new record
#                             timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
#                             scan_count = 1  # Example scan count
#                             sql_insert_query = "INSERT INTO products_info (EAN_13, Status, Timestamp, Scan_Count) VALUES (%s, %s, %s, %s)"
#                             cursor.execute(sql_insert_query, (ean_13, selected_status, timestamp, scan_count))
#                             db_connection.commit()
#                             print("Successfully inserted", selected_status)
#                             used_codes.add(decoded_data)
#                             response['results'].append({'product_id': ean_13})
#                             run_camera_thread = False

#                         else:
#                             print('Sorry, this code has been used')
#                             product_info = retrieve_product_info(decoded_data)
#                             if product_info:
#                                 print("Result:", decoded_data, product_info[0], product_info[1])
#             else:
#                 cv2.imshow('Testing-code-scan', frame)
#                 cv2.waitKey(1)
#     except Exception as e:
#         print("Error:", str(e))
#         response['error'] = str(e)
#     finally:
#         if 'cursor' in locals():
#             cursor.close()
#         if 'db_connection' in locals():
#             db_connection.close()
#         if 'cap' in locals():
#             cap.release()
#             cv2.destroyAllWindows()

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')