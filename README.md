# Automobile Shop Data Analytics Web App

A Flask-based web application for managing and analyzing customer purchases in an automobile shop. This project supports both customers and shop owners with insightful analytics, purchase tracking, interactive charts, and RFM-based customer segmentation.

---

##  Features

### Customer Panel
-  Register and login securely
-  Add new purchase records
-  View complete purchase history
-  View personal summary:
  - Total amount spent
  - Number of purchases
  - Average purchase value
  - Preferred category
  - RFM scores and customer classification
-  Interactive charts:
  - Spending Over Time
  - Category-wise Spending

---

### 👑 Owner Panel
-  Secure owner login using username & password
-  View and filter all customer purchases
-  Customer leaderboard by spending and frequency
-  RFM Analysis with downloadable charts
-  Download reports (CSV) for:
  - Filtered purchases
  - Complete customer summary
  - RFM metrics

---

## 🛠 Tech Stack

- **Frontend**: HTML5, Bootstrap 5 (Dark + Red Theme)
- **Backend**: Python (Flask Framework)
- **Database**: MySQL (via XAMPP)
- **Data Analysis**: Pandas
- **Visualization**: Matplotlib
- **Authentication**: Flask session-based login system

---
## 🗄️ Database Setup

1. Use XAMPP and open **phpMyAdmin**.
2. Create a database named `automobile_shop`.

---

Owner Access Notes
Unlike customers, owners are not registered through the web app.

To add an owner, manually insert owner credentials into the owners table in the database.

Owner login uses:

Username (e.g., bansuri)

Password (e.g., 8805)

---


##  Getting Started

###  Prerequisites

- Python 3.x
- MySQL (XAMPP or standalone)
- pip package manager

###  Installation

```bash
# Clone the repository
git https://github.com/KrishDhebariya009/automobile-shop-analytics.git
cd automobile-shop

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py


