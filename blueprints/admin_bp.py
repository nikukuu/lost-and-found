from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app, send_file
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import random
import string
from captcha.image import ImageCaptcha
import sys
import os
admin_bp = Blueprint('admin', __name__, template_folder='../templates')

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='lafsample'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return None
    
def log_activity(admin_username, action):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = "INSERT INTO activity_logs (admin_username, action) VALUES (%s, %s)"
    cursor.execute(query, (admin_username, action))

    connection.commit()
    cursor.close()
    connection.close()


#----------------------------ADMIN---LOGIN------------------------------------------------------------------------

# Helper: Generate CAPTCHA text
def generate_captcha_text(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

#----------------------------ADMIN---LOGIN------------------------------------------------------------------------

@admin_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        captcha_input = request.form['captcha']

        if captcha_input.upper() != session.get('captcha_text', ''):
            flash('Invalid CAPTCHA', 'danger')
            return redirect(url_for('admin.admin_login'))

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT username, password FROM admin_info WHERE id = 1")
        admin = cursor.fetchone()
        cursor.close()
        connection.close()

        if admin and admin[0] == username and check_password_hash(admin[1], password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    session['captcha_text'] = generate_captcha_text()
    return render_template('admin_login.html')

# CAPTCHA image route
@admin_bp.route('/admin_login/captcha')
def captcha_image():
    image = ImageCaptcha()
    captcha_text = session.get('captcha_text', '')
    data = image.generate(captcha_text)
    return send_file(data, mimetype='image/png')
@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin.admin_login'))

@admin_bp.route('/admin_account', methods=['GET', 'POST'])
def admin_account():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    success_message = None
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']

        # Validate inputs
        if len(new_username.strip()) == 0 or len(new_username) > 100:
            flash("Invalid username. Must be 1-100 characters.", 'danger')
        elif len(new_password.strip()) < 6:
            flash("Password must be at least 6 characters.", 'danger')
        else:
            # Update the credentials in the database
            hashed_password = generate_password_hash(new_password)
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE admin_info SET username = %s, password = %s WHERE id = 1",
                (new_username, hashed_password)
            )
            connection.commit()
            cursor.close()
            connection.close()

            success_message = "Admin credentials updated successfully!"

    return render_template('admin_account.html', success_message=success_message)

#----------------------------CONTACT US FORM (Moved from contact_us_bp.py)----------------------------

@admin_bp.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    success_message = None

    if request.method == 'POST':
        # Retrieve form data
        item_id = request.form['item_id']
        claimer_name = request.form['claimer_name']
        contact_info = request.form['contact_info']
        message = request.form['message']

        # Validate inputs
        if not item_id.isdigit() or int(item_id) < 1:
            flash("Invalid Item ID. Must be a positive number.", 'danger')
            return render_template('contact_us.html')

        if len(claimer_name.strip()) == 0 or len(claimer_name) > 100:
            flash("Invalid Claimer Name. Must be 1-100 characters.", 'danger')
            return render_template('contact_us.html')

        if len(contact_info.strip()) == 0 or len(contact_info) > 150:
            flash("Invalid Contact Info. Must be 1-150 characters.", 'danger')
            return render_template('contact_us.html')

        if len(message) > 500:
            flash("Message too long. Max 500 characters.", 'danger')
            return render_template('contact_us.html')

        # Insert into database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO claims (item_id, claimer_name, contact_info, message) VALUES (%s, %s, %s, %s)",
            (item_id, claimer_name, contact_info, message)
        )
        connection.commit()
        cursor.close()
        connection.close()

        success_message = "Claimer Info Submitted"

    return render_template('contact_us.html', success_message=success_message)

#--------------------------ADMIN---DASHBOARD--------------------------------------------

@admin_bp.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Get published and claimed item counts
    cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'Published'")
    published_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM items WHERE status = 'Claimed'")
    claimed_count = cursor.fetchone()[0]

    # Fetch the summary of posted items
    cursor.execute("""
        SELECT id, item_name, date_found, status 
        FROM items
        ORDER BY date_found DESC
    """)
    posted_items = cursor.fetchall()

    # Fetch details of claims*
    cursor.execute("""
        SELECT claims.id, items.item_name, claims.claimer_name, claims.contact_info, claims.status, claims.message, claims.date_claimed
        FROM claims
        INNER JOIN items ON claims.item_id = items.id
        ORDER BY claims.date_claimed DESC
    """)
    claims = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'admin_dashboard.html',
        published_count=published_count,
        claimed_count=claimed_count,
        posted_items=posted_items,
        claims=claims
    )

#---------------------ITEMS------------------------------------------------------------------------------

@admin_bp.route('/admin_post', methods=['GET', 'POST'])
def admin_post():
    success_message = None

    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        location = request.form['location']
        date_found = datetime.now().date()

        # Handle image file upload
        image_file = request.files['image']
        image_path = None
        
        # Function to check allowed file extensions
        def allowed_file(filename):
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)

            # Define the full path to save the file
            full_path = os.path.join(current_app.static_folder, 'uploads', filename)

            # Save the file to the uploads directory
            os.makedirs(os.path.dirname(full_path), exist_ok=True)  # Ensure the directory exists
            image_file.save(full_path)

            image_path = filename  # Only store the filename in the database

        # Save data to the database using raw SQL
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO items (item_name, description, location, date_found, status, image_path) VALUES (%s, %s, %s, %s, %s, %s)",
            (item_name, description, location, date_found, 'published', image_path)  # Set status to 'published'
        )
        connection.commit()
        cursor.close()
        connection.close()

        log_activity(session['admin_username'], f"Posted new item: {item_name}")

        success_message = "Post Item successfully published."

    return render_template('admin_post.html', success_message=success_message)

@admin_bp.route('/admin_items')
def admin_items():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    status_filter = request.args.get('status')  # Get status from query string

    connection = get_db_connection()
    cursor = connection.cursor()

    if status_filter in ['published', 'claimed']:
        cursor.execute("""
            SELECT id, date_found, item_name, description, status 
            FROM items 
            WHERE status = %s 
            ORDER BY date_found DESC, id ASC
        """, (status_filter,))
    else:
        cursor.execute("""
            SELECT id, date_found, item_name, description, status 
            FROM items 
            ORDER BY date_found DESC, id ASC
        """)

    items = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin_items.html', items=items, selected_status=status_filter)


@admin_bp.route('/admin/claims')
def admin_claims():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, item_id, claimer_name, contact_info, status, message, date_claimed 
        FROM claims 
        ORDER BY date_claimed DESC, id ASC
    """)
    claims = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin_claims.html', claims=claims)

@admin_bp.route('/admin/confirm_claim/<int:claim_id>', methods=['POST'])
def confirm_claim(claim_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    # Default description for claimed items
    default_description = "Claimed the item here at the Main Office of ISU-CC"

    # Establish database connection
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Update claim status to 'confirmed' and set the date_claimed
        cursor.execute(
            """
            UPDATE claims 
            SET date_claimed = %s, status = 'confirmed' 
            WHERE id = %s
            """,
            (datetime.now(), claim_id)
        )

        # Fetch the item_id associated with this claim
        cursor.execute("SELECT item_id FROM claims WHERE id = %s", (claim_id,))
        result = cursor.fetchone()
        
        if result:
            item_id = result[0]

            # Update the corresponding item status to 'claimed' and set description
            cursor.execute(
                """
                UPDATE items 
                SET status = 'Claimed', description = %s 
                WHERE id = %s
                """,
                (default_description, item_id)
            )

            log_activity(session['admin_username'], f"Confirmed claim ID {claim_id} and marked item ID {item_id} as claimed.")

            # Commit the changes to the database
            connection.commit()
            flash('Claim confirmed successfully!', 'success')
        else:
            flash('Invalid claim ID. Item not found.', 'danger')

    except Exception as e:
        connection.rollback()
        flash(f'Error confirming claim: {e}', 'danger')

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin.admin_claims'))


@admin_bp.route('/admin/claims/delete/<int:claim_id>', methods=['POST'])
def delete_claim(claim_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Delete the claim with the specified ID
    cursor.execute("DELETE FROM claims WHERE id = %s", (claim_id,))
    connection.commit()

    cursor.close()
    connection.close()

    log_activity(session['admin_username'], f"Deleted claim ID {claim_id}")

    flash(f"Claim ID {claim_id} has been successfully deleted.", 'success')
    return redirect(url_for('admin.admin_claims'))

@admin_bp.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        # Get updated details from the form
        item_name = request.form['name']
        description = request.form['description']
        status = request.form['status']

        # Update the item in the database
        cursor.execute("""
            UPDATE items
            SET item_name = %s, description = %s, status = %s
            WHERE id = %s
        """, (item_name, description, status, item_id))
        connection.commit()

        cursor.close() 
        connection.close()

        log_activity(session['admin_username'], f"Edited item ID {item_id}")
        
        flash('Item updated successfully!', 'success')
        return redirect(url_for('admin.admin_items'))

    # For GET: Fetch the current details of the item
    cursor.execute("""
        SELECT id, item_name, description, status 
        FROM items 
        WHERE id = %s
    """, (item_id,))
    item = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('edit_item.html', item=item)

@admin_bp.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Delete the item from the database
        cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
        connection.commit()

        flash('Item deleted successfully!', 'success')
    except Exception as e:
        connection.rollback()
        flash(f'Error deleting item: {e}', 'danger')
    finally:
        cursor.close()
        connection.close()

        log_activity(session['admin_username'], f"Deleted item ID {item_id}")

    return redirect(url_for('admin.admin_items'))


#------------------------Activity Logs---------------------------------

@admin_bp.route('/admin_logs')
def admin_logs():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.admin_login'))

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT admin_username, action, timestamp FROM activity_logs ORDER BY timestamp DESC")
    logs = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin_logs.html', logs=logs)
