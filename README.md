---
title: Sales & Customer Dashboard
emoji: 📊
colorFrom: purple
colorTo: blue
sdk: docker
sdk_version: "latest"
app_file: app.py
pinned: false
---

# 📊 Sales & Customer Dashboard

An **interactive and colorful Dash dashboard** for analyzing
**E-commerce Sales and Customer Behavior**.\
Built with **Python, Dash, Plotly, and Pandas**, and deployed on
**Hugging Face Spaces**.

------------------------------------------------------------------------

## 🚀 Live Demo

👉 **Hugging Face App:**\
`https://huggingface.co/spaces/YOUR_USERNAME/dash-sales-dashboard`

*(Replace `YOUR_USERNAME` with your Hugging Face username after
deployment.)*

------------------------------------------------------------------------

## ✨ Features

-   📈 **Sales Over Time Analysis**
-   🌍 **Global Revenue Map (Country-wise)**
-   🛍️ **Category & Product Insights**
-   👥 **Customer Analytics (Gender, Referral, Session Behavior)**
-   🎯 **Key KPIs**
    -   Total Revenue\
    -   Total Orders\
    -   Unique Customers\
    -   Average Order Value\
-   🔎 **Interactive Filters**
    -   Country\
    -   Category\
    -   Date Range\
-   💾 **Download Filtered CSV**
-   🎨 **Modern UI with Gradient Styling**

------------------------------------------------------------------------

## 🧰 Tech Stack

-   **Python**
-   **Dash & Plotly**
-   **Pandas**
-   **HTML / CSS**
-   **Hugging Face Spaces (Deployment)**

------------------------------------------------------------------------

## 📂 Project Structure

    dash-sales-dashboard/
    │
    ├── app.py
    ├── requirements.txt
    ├── README.md
    └── data/
        └── ecommerce_synthetic_dataset.csv

------------------------------------------------------------------------

## ⚙️ Run Locally

### 1️⃣ Clone the repository

    git clone https://github.com/YOUR_GITHUB_USERNAME/dash-sales-dashboard.git
    cd dash-sales-dashboard

### 2️⃣ Install dependencies

    pip install -r requirements.txt

### 3️⃣ Run the app

    python app.py

### 4️⃣ Open in browser

    http://127.0.0.1:8000

------------------------------------------------------------------------

## 🤗 Deploy on Hugging Face Spaces

### Step 1: Create a new Space

-   Go to 👉 https://huggingface.co/spaces\
-   Click **Create new Space**
-   Space Name: `dash-sales-dashboard`
-   SDK: **Docker**
-   Visibility: Public

------------------------------------------------------------------------

### Step 2: Upload project files

Upload these files into your Space:

    app.py
    requirements.txt
    data/ecommerce_synthetic_dataset.csv

------------------------------------------------------------------------

### Step 3: Ensure app runs on Hugging Face port

In `app.py`, confirm this:

``` python
if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=7860)
```

------------------------------------------------------------------------

### Step 4: Wait for build

Hugging Face will automatically: - Install dependencies - Build
environment - Launch your Dash app

------------------------------------------------------------------------

### Step 5: Access your live dashboard

    https://huggingface.co/spaces/YOUR_USERNAME/dash-sales-dashboard

🎉 Your dashboard is now live!



------------------------------------------------------------------------

## 👨‍💻 Author

**Samir Biswakarma**\
Data Analytics

------------------------------------------------------------------------

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

------------------------------------------------------------------------

## 📜 License

This project is open-source and free to use.
