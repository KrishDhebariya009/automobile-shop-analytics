from flask import Flask, render_template, request, redirect, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import database_conn
from datetime import datetime
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
import seaborn as sns
import io





app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Required for session to work



@app.route('/home')
def home():
    
    if 'user_id' not in session:
        flash("🔒 Please login first.")
        return redirect('/login')

    return render_template('home.html', name=session['user_name'])

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@app.route('/logout')
def logout():
    session.clear()
    flash("👋 Logged out successfully.")
    return redirect('/login')



@app.route('/download_rfm_csv', methods=['POST'])
def download_rfm_csv():
    if 'user_id' not in session or session.get('role') != 'owner':
        flash("🚫 Only the owner can download this.")
        return redirect('/home')

    conn = database_conn.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, mobile, amount, date FROM purchases")
    data = cur.fetchall()
    cur.close()
    conn.close()

    df = pd.DataFrame(data, columns=['name', 'mobile', 'amount', 'date'])
    df['date'] = pd.to_datetime(df['date'])
    today = pd.to_datetime('today')

    rfm = df.groupby(['name', 'mobile']).agg({
        'date': lambda x: (today - x.max()).days,
        'mobile': 'count',
        'amount': 'sum'
    })
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    rfm = rfm.reset_index()

    # Save CSV temporarily
    csv_path = 'static/data/rfm_report.csv'
    rfm.to_csv(csv_path, index=False)

    return send_file(csv_path, as_attachment=True)

@app.route('/download_history_csv', methods=['POST'])
def download_history_csv():
    if 'user_id' not in session:
        flash("🔒 Please login to download history.")
        return redirect('/login')

    user_id = session['user_id']

    conn = database_conn.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT bill_no, amount, category, vehicle, payment, date FROM purchases WHERE user_id = %s", (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Save to CSV temporarily
    import pandas as pd
    import os

    df = pd.DataFrame(rows, columns=['Bill No', 'Amount', 'Category', 'Vehicle', 'Payment', 'Date'])

    # Ensure folder exists
    if not os.path.exists('static/data'):
        os.makedirs('static/data')

    file_path = f'static/data/history_user_{user_id}.csv'
    df.to_csv(file_path, index=False)

    return send_file(file_path, as_attachment=True)

@app.route('/download_filtered_csv', methods=['POST'])
def download_filtered_csv():
    if 'user_id' not in session or session.get('role') != 'owner':
        flash("🚫 Only owner can download.")
        return redirect('/home')

    filters = []
    values = []

    mobile = request.form.get('mobile')
    category = request.form.get('category')
    vehicle = request.form.get('vehicle')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    if mobile:
        filters.append("mobile = %s")
        values.append(mobile)
    if category and category != 'All':
        filters.append("category = %s")
        values.append(category)
    if vehicle and vehicle != 'All':
        filters.append("vehicle = %s")
        values.append(vehicle)
    if start_date:
        filters.append("date >= %s")
        values.append(start_date)
    if end_date:
        filters.append("date <= %s")
        values.append(end_date)

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT name, mobile, bill_no, amount, category, vehicle, payment, date 
        FROM purchases
        {where_clause}
        ORDER BY date DESC
    """

    conn = database_conn.get_connection()
    cur = conn.cursor()
    cur.execute(query, tuple(values))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    # Save to CSV
    import pandas as pd
    import os
    from flask import send_file

    df = pd.DataFrame(rows, columns=['Name', 'Mobile', 'Bill No', 'Amount', 'Category', 'Vehicle', 'Payment', 'Date'])

    if not os.path.exists('static/data'):
        os.makedirs('static/data')

    file_path = 'static/data/filtered_purchases.csv'
    df.to_csv(file_path, index=False)

    return send_file(file_path, as_attachment=True)


@app.route('/my_summary')
def my_summary():
    if 'user_id' not in session:
        flash("Please login to view your summary.")
        return redirect('/login')

    mobile = session.get('mobile')

    conn = database_conn.get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT name, mobile, amount, category, date
        FROM purchases
        WHERE mobile = %s
        ORDER BY date DESC
    """, (mobile,))
    data = cur.fetchall()
    cur.close()
    conn.close()

    if not data:
        flash("No purchases found.")
        return redirect('/home')

    import pandas as pd
    from datetime import datetime

    df = pd.DataFrame(data, columns=['Name', 'Mobile', 'Amount', 'Category', 'Date'])
    df['Date'] = pd.to_datetime(df['Date'])
    now = pd.to_datetime(datetime.now())

    # Grouped summary for this customer
    summary = {
        'Name': df['Name'].iloc[0],
        'Mobile': mobile,
        'Total_Amount': df['Amount'].sum(),
        'Purchase_Count': df['Amount'].count(),
        'Avg_Purchase': round(df['Amount'].mean(), 2),
        'Preferred_Category': df['Category'].mode()[0] if not df['Category'].mode().empty else 'N/A',
        'First_Purchase': df['Date'].min().date(),
        'Last_Purchase': df['Date'].max().date(),
        'Recency': (now - df['Date'].max()).days,
        'Frequency': df['Amount'].count(),
        'Monetary': df['Amount'].sum(),
    }

    # Classify customer type
    if summary['Recency'] <= 10 and summary['Frequency'] >= 3:
        summary['Customer_Type'] = 'Loyal'
    elif summary['Monetary'] > 3000:
        summary['Customer_Type'] = 'Big Spender'
    elif summary['Recency'] > 30:
        summary['Customer_Type'] = 'At Risk'
    else:
        summary['Customer_Type'] = 'Regular'

    return render_template('my_summary.html', summary=summary)





@app.route('/all_purchases', methods=['GET', 'POST'])
def all_purchases():
    if 'user_id' not in session or session.get('role') != 'owner':
        flash("🚫 Only the owner can access all purchase records.")
        return redirect('/home')

    filters = []
    values = []

    if request.method == 'POST':
        mobile = request.form.get('mobile')
        category = request.form.get('category')
        vehicle = request.form.get('vehicle')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        if mobile:
            filters.append("mobile = %s")
            values.append(mobile)
        if category and category != 'All':
            filters.append("category = %s")
            values.append(category)
        if vehicle and vehicle != 'All':
            filters.append("vehicle = %s")
            values.append(vehicle)
        if start_date:
            filters.append("date >= %s")
            values.append(start_date)
        if end_date:
            filters.append("date <= %s")
            values.append(end_date)

    where_clause = "WHERE " + " AND ".join(filters) if filters else ""

    query = f"""
        SELECT name, mobile, bill_no, amount, category, vehicle, payment, date 
        FROM purchases
        {where_clause}
        ORDER BY date DESC
    """

    
    conn = database_conn.get_connection()
    cur = conn.cursor()
    cur.execute(query, tuple(values))
    purchases = cur.fetchall()

    # Summary Stats
    total_sales = sum(row[3] for row in purchases)
    total_purchases = len(purchases)
    unique_customers = len(set(row[1] for row in purchases))  # mobile numbers

    cur.close()
    conn.close()

    return render_template(
        'all_purchases.html',
        purchases=purchases,
        total_sales=total_sales,
        total_purchases=total_purchases,
        unique_customers=unique_customers
    )

@app.route('/download_customer_report')
def download_customer_report():
    if 'user_id' not in session or session.get('role') != 'owner':
        flash("🚫 Only the owner can download reports.")
        return redirect('/home')

    conn = database_conn.get_connection()
    cur = conn.cursor()

    # Fetch data
    cur.execute("""
        SELECT name, mobile, amount, category, date
        FROM purchases
        ORDER BY date DESC
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()

    df = pd.DataFrame(data, columns=['Name', 'Mobile', 'Amount', 'Category', 'Date'])

    # Fix Decimal → float
    df['Amount'] = df['Amount'].astype(float)
    df['Date'] = pd.to_datetime(df['Date'])


    # Grouped stats
    now = pd.to_datetime(datetime.now())
    grouped = df.groupby('Mobile').agg({
        'Name': 'first',
        'Amount': ['sum', 'count', 'mean'],
        'Category': lambda x: x.mode()[0] if not x.mode().empty else 'N/A',
        'Date': ['min', 'max']
    })

    grouped.columns = [
        'Name', 'Total_Amount', 'Purchase_Count', 'Avg_Purchase',
        'Preferred_Category', 'First_Purchase', 'Last_Purchase'
    ]
    grouped = grouped.reset_index()

    grouped['Recency'] = (now - grouped['Last_Purchase']).dt.days
    grouped['Frequency'] = grouped['Purchase_Count']
    grouped['Monetary'] = grouped['Total_Amount']

    # --- Safe RFM scorer ---
    def safe_qcut(series, labels_desc):
        unique_vals = series.nunique()
    
        if unique_vals < 2:
            default = labels_desc[len(labels_desc) // 2]
            return pd.Series([default] * len(series), index=series.index)
        
        q = min(len(labels_desc), unique_vals)
        
        cat = pd.qcut(series, q=q, duplicates='drop')
        codes = pd.Categorical(cat).codes + 1  # Convert to 1-based scores
        
        return pd.Series(codes, index=series.index)


    grouped['R'] = safe_qcut(grouped['Recency'], [5, 4, 3, 2, 1])
    grouped['F'] = safe_qcut(grouped['Frequency'], [1, 2, 3, 4, 5])
    grouped['M'] = safe_qcut(grouped['Monetary'], [1, 2, 3, 4, 5])

    def classify(row):
        if row['R'] >= 4 and row['F'] >= 4:
            return 'Loyal'
        elif row['R'] >= 4 and row['M'] >= 4:
            return 'Big Spender'
        elif row['R'] <= 2:
            return 'At Risk'
        elif row['F'] == 1:
            return 'New'
        else:
            return 'Regular'

    grouped['Customer_Type'] = grouped.apply(classify, axis=1)

    # Save to CSV
    if not os.path.exists('static/reports'):
        os.makedirs('static/reports')
    file_path = 'static/reports/advanced_customer_report.csv'
    grouped.to_csv(file_path, index=False)

    return send_file(file_path, as_attachment=True)



@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session or session.get('role') != 'owner':
        flash("🚫 Only the owner can view the leaderboard.")
        return redirect('/home')

    conn = database_conn.get_connection()
    cur = conn.cursor()

    # 🥇 Top by total purchase amount
    cur.execute("""
        SELECT name, mobile, COUNT(*) AS purchase_count, SUM(amount) AS total_amount
        FROM purchases
        GROUP BY mobile
        ORDER BY total_amount DESC
        LIMIT 5
    """)
    top_amount = cur.fetchall()

    # 🔁 Top by frequency
    cur.execute("""
        SELECT name, mobile, COUNT(*) AS purchase_count, SUM(amount) AS total_amount
        FROM purchases
        GROUP BY mobile
        ORDER BY purchase_count DESC
        LIMIT 5
    """)
    top_frequency = cur.fetchall()

    cur.close()
    conn.close()

    return render_template('leaderboard.html',
                           top_amount=top_amount,
                           top_frequency=top_frequency)


@app.route('/history')
def history():
    if 'user_id' not in session:
        flash("🔒 Please login to view your history.")
        return redirect('/login')

    user_id = session['user_id']
    conn = database_conn.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT bill_no, amount, category, vehicle, payment, date FROM purchases WHERE user_id = %s ORDER BY date DESC", (user_id,))
    purchases = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('history.html', purchases=purchases)

@app.route('/customer_charts')
def customer_charts():
    if 'user_id' not in session or session.get('role') != 'customer':
        flash("Access denied.")
        return redirect('/home')

    conn = database_conn.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, amount, category
        FROM purchases
        WHERE mobile = %s
        ORDER BY date
    """, (session['mobile'],))
    data = cur.fetchall()
    cur.close()
    conn.close()

    if not data:
        flash("No purchase data available to display charts.")
        return redirect('/home')

    # Prepare DataFrame
    df = pd.DataFrame(data, columns=['Date', 'Amount', 'Category'])
    df['Date'] = pd.to_datetime(df['Date'])


    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')  # convert and handle bad values
    df = df.dropna(subset=['Amount'])  # drop rows where amount could not be converted


    # 1️⃣ Spending Over Time - Line Chart
    line_data = df.groupby('Date')['Amount'].sum()

    plt.figure(figsize=(6, 3))
    line_data.plot(kind='line', marker='o', color='orange')
    plt.title('Spending Over Time')
    plt.xlabel('Date')
    plt.ylabel('Amount (₹)')
    plt.tight_layout()
    buffer1 = BytesIO()
    plt.savefig(buffer1, format='png')
    buffer1.seek(0)
    line_chart = base64.b64encode(buffer1.read()).decode('utf-8')
    plt.close()

    # 2️⃣ Category-wise Spending - Pie Chart
    pie_data = df.groupby('Category')['Amount'].sum()

    plt.figure(figsize=(4, 4))
    pie_data.plot(kind='pie', autopct='%1.1f%%', startangle=90)
    plt.title('Category-wise Spending')
    plt.ylabel('')
    plt.tight_layout()
    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    pie_chart = base64.b64encode(buffer2.read()).decode('utf-8')
    plt.close()

    return render_template('customer_charts.html',
                           line_chart=line_chart,
                           pie_chart=pie_chart)


@app.route('/rfm', methods=['GET', 'POST'])
def rfm():
    if 'user_id' not in session or session.get('role') != 'owner':
        flash("🚫 Access denied. Only owner can view RFM.")
        return redirect('/home')

    conn = database_conn.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, mobile, amount, date FROM purchases")
    data = cur.fetchall()
    cur.close()
    conn.close()

    

    df = pd.DataFrame(data, columns=['name', 'mobile', 'amount', 'date'])
    df['date'] = pd.to_datetime(df['date'])
    today = pd.to_datetime('today')

    rfm_df = df.groupby(['name', 'mobile']).agg({
        'date': lambda x: (today - x.max()).days,
        'mobile': 'count',
        'amount': 'sum'
    })
    rfm_df.columns = ['Recency', 'Frequency', 'Monetary']
    rfm_df = rfm_df.reset_index()

    chart_data = None
    chart_type = None

    if request.method == 'POST':
        chart_type = request.form.get('chart')

        if chart_type == 'top':
            top_customers = rfm_df.sort_values(by='Monetary', ascending=False).head(5)
            plt.figure(figsize=(8, 5))
            sns.barplot(x='Monetary', y='name', data=top_customers, palette='mako')
            plt.title('Top 5 Customers by Spending')
            plt.xlabel('Total Amount (₹)')
            plt.ylabel('Customer Name')
        elif chart_type == 'recency':
            plt.figure(figsize=(8, 4))
            sns.histplot(rfm_df['Recency'], bins=10, kde=True, color='orange')
            plt.title('Recency Distribution')
            plt.xlabel('Days Since Last Purchase')

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        chart_data = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

    return render_template('rfm.html', rfm=rfm_df.to_dict(orient='records'),
                           chart_data=chart_data, chart_type=chart_type)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect('/home')

    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        password = request.form['password']
        hashed_password = generate_password_hash(password)


        conn = database_conn.get_connection()
        cur = conn.cursor()

        # Check if mobile already exists
        cur.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("❌ Mobile number already registered!")
            return redirect('/register')

        # Insert new user
        cur.execute("INSERT INTO users (name, mobile, password) VALUES (%s, %s, %s)",
            (name, mobile, hashed_password))
        conn.commit()
        cur.close()
        conn.close()

        flash("✅ Registration successful! Please login.")
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/home')

    if request.method == 'POST':
        identifier = request.form['mobile']  # can be owner name or customer mobile
        password = request.form['password']

        conn = database_conn.get_connection()
        cur = conn.cursor()

        # ✅ Check if it's an owner login (match by name)
        cur.execute("SELECT id, name, password FROM owners WHERE name = %s", (identifier,))
        owner = cur.fetchone()

        if owner and owner[2] == password:
            session['user_id'] = owner[0]
            session['user_name'] = owner[1]
            session['mobile'] = 'owner_login'
            session['role'] = 'owner'
            cur.close()
            conn.close()

            flash("👑 Owner login successful!")
            return redirect('/home')

        # ✅ If not owner, check customer (match by mobile)
        cur.execute("SELECT id, name, password FROM users WHERE mobile = %s", (identifier,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['mobile'] = identifier
            session['role'] = 'customer'

            flash("✅ Customer login successful!")
            return redirect('/home')
        else:
            flash("❌ Invalid credentials.")
            return redirect('/login')

    return render_template('login.html')




@app.route('/')
def index():
    return redirect('/home')

@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if 'user_id' not in session:
        flash("🔒 Login required to add purchase.")
        return redirect('/login')

    if request.method == 'POST':
        bill = request.form['bill']
        name = session['user_name']
        mobile = session['mobile']
        amount = float(request.form['amount'])
        category = request.form['category']
        vehicle = request.form['vehicle']
        payment = request.form['payment']
        date = datetime.now().strftime('%Y-%m-%d')
        user_id = session['user_id']

        # Save to CSV
        with open('data/purchase_data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([bill, name, mobile, amount, category, vehicle, payment, date])

        # Save to MySQL
        conn = database_conn.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO purchases (user_id, bill_no, name, mobile, amount, category, vehicle, payment, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, bill, name, mobile, amount, category, vehicle, payment, date))
        conn.commit()
        cur.close()
        conn.close()

        flash("✅ Purchase saved successfully.")
        return redirect('/home')

    return render_template('adding_record.html')




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

