from flask import*
import mysql.connector
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)

app.secret_key = os.urandom(24)

# Set folder to save uploaded product images
app.config['UPLOAD_FOLDER'] = 'static/images'

# Allowed extensions for image uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check if the file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to get a database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Add your password if set
        database="rider_db"
    )

# Dashboard route and all graphs 
@app.route('/')
def dashboard():
    db = get_db_connection()
    cursor = db.cursor()

    # Query for riders count by 'submitted_by'
    cursor.execute("""
        SELECT submitted_by, COUNT(rider_id) 
        FROM riders 
        GROUP BY submitted_by
    """)
    submitted_by_data = cursor.fetchall()

    # Query for riders count by 'lead_classification'
    cursor.execute("""
        SELECT lead_classification, COUNT(rider_id) 
        FROM riders 
        GROUP BY lead_classification
    """)
    lead_classification_data = cursor.fetchall()
    
       # 1. Total Riders (Banner)
    cursor.execute("SELECT COUNT(*) FROM riders")
    total_riders = cursor.fetchone()[0]

    # 2. Riders by Location
    cursor.execute("SELECT work_location, COUNT(rider_id) FROM riders GROUP BY work_location")
    location_data = cursor.fetchall()  # Each row will contain (location, total)

    # 3. Riders by Loan Status
    cursor.execute("SELECT any_pending_loan, COUNT(rider_id) FROM riders GROUP BY any_pending_loan")
    loan_status_data = cursor.fetchall()  # Each row will contain (loan_status, total)

    # Convert loan status from 0/1 to meaningful labels
    loan_status_labels = ['No Loan', 'Has Loan']
    loan_status_data = [(loan_status_labels[status[0]], status[1]) for status in loan_status_data]
    # Fetch total riders
    cursor.execute("SELECT COUNT(*) FROM riders")
    total_riders = cursor.fetchone()[0]

    # Fetch lead classification counts for Pie and Funnel Chart
    cursor.execute("""
        SELECT lead_classification, COUNT(*) 
        FROM riders 
        GROUP BY lead_classification
    """)
    lead_classification_data = cursor.fetchall()
    
    # Ensure we always have data
    if not lead_classification_data:
        lead_classification_labels = []
        lead_classification_counts = []
    else:
        lead_classification_labels = [item[0] for item in lead_classification_data]
        lead_classification_counts = [item[1] for item in lead_classification_data]

    # Extracting funnel data based on lead classification stages
    funnel_data = {
        "hot": next((count for label, count in lead_classification_data if label == "hot"), 0),
        "warm": next((count for label, count in lead_classification_data if label == "warm"), 0),
        "cold": next((count for label, count in lead_classification_data if label == "cold"), 0),
    }
    
    funnel_labels = list(funnel_data.keys())
    funnel_counts = list(funnel_data.values())
    
    # deals_analytics
        # Fetch the total number of deals
    cursor.execute("SELECT COUNT(deal_id) AS total_deals FROM deals")
    total_deals_count = cursor.fetchone()[0]  # Get the count from the first row
           # Fetch deals submitted by counts from the riders table
    cursor.execute("""
        SELECT r.submitted_by, COUNT(d.deal_id) AS deal_count
        FROM deals AS d
        JOIN riders AS r ON d.rider_id = r.rider_id
        GROUP BY r.submitted_by
    """)
    submitted_by_data = cursor.fetchall()
    
    # Prepare the data for the chart
    submitted_by_labels = [data[0] for data in submitted_by_data]  # Extract names
    submitted_by_counts = [data[1] for data in submitted_by_data]  # Extract deal counts

    # Fetch products and their corresponding deal counts
    cursor.execute("""
        SELECT p.product_name, COUNT(d.product_id) AS deal_count
        FROM products AS p
        LEFT JOIN deals AS d ON p.product_id = d.product_id
        GROUP BY p.product_name
    """)
    products_data = cursor.fetchall()

    products = [data[0] for data in products_data]  # Product names
    product_counts = [data[1] for data in products_data]  # Deal counts for each product

    cursor.close()
    db.close()

    return render_template('dashboard.html', 
                           submitted_by_data=submitted_by_data, 
                           lead_classification_data=lead_classification_data,
                           total_riders=total_riders, 
                           location_data=location_data, 
                           loan_status_data=loan_status_data,
                            lead_classification_labels=lead_classification_labels,
                            lead_classification_counts=lead_classification_counts,
                            funnel_labels=funnel_labels,
                            funnel_counts=funnel_counts, 
                            # deals 
                            total_deals_count=total_deals_count,
                           submitted_by_labels=submitted_by_labels, 
                           submitted_by_counts=submitted_by_counts, 
                           products=products, 
                           product_counts=product_counts
                           )

# Fetch total riders
@app.route('/totalRiders')
def total_riders():

    return render_template('totalRiders.html')

# Analytics Route
@app.route('/ridersAnalytics')
def riders_analytics():
    db = get_db_connection()
    cursor = db.cursor()
     # 1. Total Riders (Banner)
    cursor.execute("SELECT COUNT(*) FROM riders")
    total_riders = cursor.fetchone()[0]
    
    cursor.close()
    db.close()
    
    return render_template('ridersAnalytics.html',total_riders=total_riders)

# Add Product route
@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    if request.method == 'POST':
        # Get form data
        product_name = request.form['product_name']
        product_description = request.form['product_description']
        product_image = request.files['product_image']

        # Check if the image file is valid
        if product_image and allowed_file(product_image.filename):
            filename = secure_filename(product_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            product_image.save(filepath)  # Save image to the static/images folder

            # Insert product details into the database
            db = get_db_connection()
            cursor = db.cursor()
            sql = """
                INSERT INTO products 
                (product_name, product_description, product_image, created_at)
                VALUES (%s, %s, %s, NOW())
            """
            values = (product_name, product_description, filename)
            cursor.execute(sql, values)
            db.commit()
            cursor.close()
            db.close()

            return redirect(url_for('addProduct'))  # Redirect after successful submission

    return render_template('addProduct.html')

@app.route('/get_add_product_link')
def get_add_product_link():
    # Return the HTML fragment for the "Add Product" link
    link_html = '<li><a class="dropdown-item text-white" href="#" onclick="loadContent(\'addProduct\')">Add Product</a></li>'
    print("Returning Add Product link: ", link_html)  # Log the link
    return jsonify(html=link_html)

# All Customers route
@app.route('/allCustomers', methods=['GET'])
def all_customers():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM riders ORDER BY created_at DESC")  # Fetch all riders ordered by created_at
    riders = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('all_customers.html', riders=riders)  # Ensure you have this template created

# Delete rider
@app.route('/delete_rider/<int:rider_id>', methods=['POST'])
def delete_rider(rider_id):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM riders WHERE rider_id=%s", (rider_id,))
    db.commit()
    cursor.close()
    db.close()
    return redirect(url_for('all_customers'))  # Redirect to all customers page after deletion

# Create Rider route
@app.route('/createRider', methods=['GET', 'POST'])
def createRider():
    if request.method == 'POST':
        # Retrieve form data
        customername = request.form['customername']
        phone_number = request.form['phone_number']
        work_location = request.form['work_location']
        current_motorbike = request.form['current_motorbike']
        fuel_consumption_per_day = request.form['fuel_consumption_per_day']
        
        # Check the value of any_pending_loan (dropdown) and convert to 1 or 0
        any_pending_loan = request.form.get('any_pending_loan')
        any_pending_loan = 1 if any_pending_loan == "yes" else 0

        lead_classification = request.form['lead_classification']
        any_comments = request.form['any_comments']
        submitted_by = request.form['submitted_by']

        # Insert into database
        db = get_db_connection()
        cursor = db.cursor()
        sql = """
            INSERT INTO riders 
            (customername, phone_number, work_location, current_motorbike, fuel_consumption_per_day, any_pending_loan, lead_classification, any_comments, submitted_by, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        values = (customername, phone_number, work_location, current_motorbike, fuel_consumption_per_day, any_pending_loan, lead_classification, any_comments, submitted_by)
        cursor.execute(sql, values)
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('createRider'))

    return render_template('createRider.html')


# Create Deal route
@app.route('/createDeal', methods=['GET', 'POST'])
def createDeal():
    error_message = None

    if request.method == 'POST':
        rider_id = request.form['rider_id']
        product_id = request.form['product_id']

        # Check if the deal already exists
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM deals WHERE rider_id = %s AND product_id = %s', (rider_id, product_id))
        existing_deal = cursor.fetchall()  # Fetch all results to avoid unread result error

        if existing_deal:
            # Deal already exists, set the error message
            error_message = "This deal already exists."
        else:
            # Insert deal into the deals table
            sql = 'INSERT INTO deals (rider_id, product_id) VALUES (%s, %s)'
            values = (rider_id, product_id)
            cursor.execute(sql, values)
            db.commit()

        cursor.close()
        db.close()

        if not error_message:
            return redirect(url_for('totalDeals'))  # Redirect to total deals page after saving     

    # Fetch riders and products for the suggestion functionality
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute('SELECT rider_id, customername FROM riders')
    riders = cursor.fetchall()
    cursor.execute('SELECT product_id, product_name FROM products')
    products = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template('createDeal.html', riders=riders, products=products, error_message=error_message)
# delete fuction for deals
@app.route('/delete_deal/<int:deal_id>', methods=['POST'])
def delete_deal(deal_id):
    try:
        db = get_db_connection()
        cursor = db.cursor()

        # Delete the deal from the database
        sql = "DELETE FROM deals WHERE deal_id = %s"
        cursor.execute(sql, (deal_id,))
        db.commit()

        cursor.close()
        db.close()

        flash("Deal deleted successfully!", "success")
    except Exception as e:
        flash("An error occurred while trying to delete the deal.", "danger")
        print(f"Error: {e}")
    return redirect(url_for('totalDeals'))   


# Suggestion route for rider names
@app.route('/suggest_riders', methods=['GET'])
def suggest_riders():
    query = request.args.get('query', '')
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT rider_id, customername FROM riders WHERE customername LIKE %s", (f'%{query}%',))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(results)

# Suggestion route for product names
@app.route('/suggest_products', methods=['GET'])
def suggest_products():
    query = request.args.get('query', '')
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT product_id, product_name FROM products WHERE product_name LIKE %s", (f'%{query}%',))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(results)

# Total Deals route
@app.route('/totalDeals')
def totalDeals():
    db = get_db_connection()
    cursor = db.cursor()

    # Select deal_id, rider_id, customername, product_name, and created_at
    cursor.execute('SELECT d.deal_id, d.rider_id, r.customername, p.product_name, d.created_at '
                   'FROM deals d '
                   'JOIN riders r ON d.rider_id = r.rider_id '
                   'JOIN products p ON d.product_id = p.product_id')
    deals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('totalDeals.html', deals=deals)

@app.route('/rider_details/<int:rider_id>')
def rider_details(rider_id):
    # Fetch the rider details from the database
    db = get_db_connection()
    cursor = db.cursor()

    # Fetch rider information
    cursor.execute("SELECT rider_id, customername, phone_number, work_location, current_motorbike, "
                   "fuel_consumption_per_day, any_pending_loan, lead_classification, any_comments, "
                   "submitted_by, created_at FROM riders WHERE rider_id = %s", (rider_id,))
    rider = cursor.fetchone()

    # Check if the rider was found
    if not rider:
        return "Rider not found", 404

    # Convert rider tuple to a dictionary for easier access in the template
    rider_columns = [column[0] for column in cursor.description]  # Get column names
    rider_dict = dict(zip(rider_columns, rider))  # Combine into a dictionary

    # Fetch the deals related to the rider, including product name
    cursor.execute("SELECT d.deal_id, p.product_name, d.created_at FROM deals d "
                   "JOIN products p ON d.product_id = p.product_id "
                   "WHERE d.rider_id = %s", (rider_id,))
    deals = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('rider_details.html', rider=rider, deals=deals)

# pipeline 
@app.route('/pipelineAnalytics', methods=['GET'])
def pipeline_analytics():
    db = get_db_connection()
    cursor = db.cursor()
    
       # Query to count total deals
    cursor.execute("SELECT COUNT(*) FROM deals")  # Ensure the 'deals' table is correct
    total_deals = cursor.fetchone()[0]  # Get the total count of deals 

    cursor.close()
    db.close()
    # Sending data to the template
    return render_template(
        'pipelineAnalytics.html',total_deals=total_deals)


@app.route('/dealsAnalytics', methods=['GET'])
def deals_analytics():
    db = get_db_connection()
    cursor = db.cursor()
    
       # Query to count total deals
    cursor.execute("SELECT COUNT(*) FROM deals")  # Ensure the 'deals' table is correct
    total_deals_count = cursor.fetchone()[0]  # Get the total count of deals 

    cursor.close()
    db.close()
    # Sending data to the template
    return render_template(
        'dealsAnalytics.html',total_deals_count=total_deals_count)


if __name__ == '__main__':
    app.run(debug=True, port=4000)