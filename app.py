# app.py
# Premium Smart Expense Tracker GUI
# Run: streamlit run app.py
from database import create_tables
from auth import register_user, login_user
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime


# PAGE CONFIG
st.set_page_config(
    page_title="Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)
create_tables()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

FILE_NAME = "expenses_data.csv"
BUDGET_FILE = "budget.txt"


# MODERN CSS UI
st.markdown("""
<style>

html, body, [class*="css"]{
    font-family: 'Segoe UI', sans-serif;
}

/* background */
.stApp{
    background: linear-gradient(to right, #eef2f3, #dfe9f3);
}

/* top heading */
.main-title{
    font-size:42px;
    font-weight:700;
    color:#0f172a;
}

.sub-text{
    color:#475569;
    font-size:17px;
    margin-bottom:20px;
}

/* cards */
.card{
    background:white;
    padding:22px;
    border-radius:18px;
    box-shadow:0 8px 20px rgba(0,0,0,0.08);
    margin-bottom:18px;
}

/* sidebar */
section[data-testid="stSidebar"]{
    background: #0f172a;
}

section[data-testid="stSidebar"] *{
    color:white;
}

/* button */
.stButton>button{
    background: linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
    border:none;
    border-radius:12px;
    height:45px;
    width:100%;
    font-size:16px;
    font-weight:600;
}

.stButton>button:hover{
    background: linear-gradient(90deg,#1d4ed8,#1e40af);
}

/* metric cards */
[data-testid="metric-container"]{
    background:white;
    border-radius:16px;
    padding:18px;
    box-shadow:0 6px 15px rgba(0,0,0,0.06);
}

</style>
""", unsafe_allow_html=True)

# DATA FUNCTIONS

def create_file():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=[
            "Date", "Category", "Amount", "Description"
        ])
        df.to_csv(FILE_NAME, index=False)

def load_data():
    create_file()
    return pd.read_csv(FILE_NAME)

def save_data(df):
    df.to_csv(FILE_NAME, index=False)
    # ---------------- Budget Functions ---------------- #

def save_budget(amount):
    with open(BUDGET_FILE, "w") as file:
        file.write(str(amount))


def load_budget():
    if os.path.exists(BUDGET_FILE):
        with open(BUDGET_FILE, "r") as file:
            return float(file.read())
    return 0

def add_expense(date, category, amount, description):
    df = load_data()

    new_row = pd.DataFrame([{
        "Date": date.strftime("%d-%m-%Y"),
        "Category": category,
        "Amount": amount,
        "Description": description
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)


# HEADER
if not st.session_state.logged_in:

    st.title("💰 Smart Expense Tracker")

    option = st.selectbox(
        "Select",
        ["Login", "Register"]
    )

    username = st.text_input("Username")

    password = st.text_input(
        "Password",
        type="password"
    )

    if option == "Register":

        confirm = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Register"):

            if password != confirm:
                st.error("Passwords do not match")

            elif register_user(username, password):
                st.success("Registration Successful")

            else:
                st.error("Username already exists")

    else:

        if st.button("Login"):

            user = login_user(username, password)

            if user:

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_id = user[0]
                st.rerun()
            else:

                st.error("Invalid Username or Password")

    st.stop()

st.markdown('<div class="main-title">💰 Smart Expense Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Track daily expenses with beautiful reports & smart insights.</div>', unsafe_allow_html=True)


# SIDEBAR

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "➕ Add Expense",
        "💰 Budget",
        "📊 Reports",
        "📋 Records"
    ]
)
st.sidebar.write("---")

if st.sidebar.button("🚪 Logout"):

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.experimental_rerun()


# DASHBOARD

if menu == "🏠 Dashboard":

    df = load_data()

    if len(df) == 0:
        st.info("No expenses added yet.")
    else:
        total = df["Amount"].sum()
        avg = df["Amount"].mean()
        top = df.groupby("Category")["Amount"].sum().idxmax()

        a, b, c = st.columns(3)

        a.metric("💸 Total Spending", f"₹{total:.2f}")
        b.metric("📈 Average Expense", f"₹{avg:.2f}")
        c.metric("🔥 Highest Category", top)

        st.markdown("### Recent Transactions")
        st.dataframe(df.tail(10), use_container_width=True)

# ADD EXPENSE

elif menu == "➕ Add Expense":

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Add New Expense")

    c1, c2 = st.columns(2)

    with c1:
        date = st.date_input("Date", datetime.today())

    with c2:
        category = st.selectbox(
            "Category",
            ["Food", "Travel", "Bills", "Shopping", "Health", "Entertainment", "Other"]
        )

    amount = st.number_input(
        "Amount",
        min_value=1.0,
        step=1.0
    )

    description = st.text_input("Description")

    if st.button("Save Expense"):
        add_expense(date, category, amount, description)
        st.success("Expense Added Successfully!")

    st.markdown('</div>', unsafe_allow_html=True)

# REPORTS
# ---------------- BUDGET ---------------- #

elif menu == "💰 Budget":

    st.subheader("💰 Monthly Budget")

    budget = float(load_budget())

    new_budget = st.number_input(
    "Set Monthly Budget",
    min_value=0.0,
    max_value=10000000.0,
    value=budget,
    step=100.0
)

    if st.button("Save Budget"):
        save_budget(new_budget)
        st.success("Budget Saved Successfully!")

    df = load_data()

    total = df["Amount"].sum() if len(df) > 0 else 0

    remaining = new_budget - total

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Budget", f"₹{new_budget:.2f}")
    col2.metric("💸 Spent", f"₹{total:.2f}")
    col3.metric("💵 Remaining", f"₹{remaining:.2f}")

    progress = 0

    if new_budget > 0:
        progress = min(total / new_budget, 1.0)

    st.progress(progress)

    if total > new_budget:
        st.error("⚠️ Budget Exceeded!")
    else:
        st.success("✅ You are within your budget.")
elif menu == "📊 Reports":

    df = load_data()

    if len(df) == 0:
        st.warning("No expense data found.")
    else:
        st.subheader("Expense Analysis")

        summary = df.groupby("Category")["Amount"].sum()

        left, right = st.columns(2)
    # 🏆 TOP 5 HIGHEST EXPENSES

        st.markdown("## 🏆 Top 5 Highest Expenses")

        top_expenses = df.sort_values(
        by="Amount",
        ascending=False
    ).head(5)
        st.dataframe(
        top_expenses,
        use_container_width=True
)
    # 📅 MONTHLY SUMMARY

    st.markdown("## 📅 Monthly Summary")
    monthly_df = df.copy()
    monthly_df["Date"] = pd.to_datetime(
        monthly_df["Date"],
        format="%d-%m-%Y"
    )
    monthly_df["Month"] = (
        monthly_df["Date"]
        .dt.strftime("%B %Y")
    )
    monthly_summary = (
        monthly_df
        .groupby("Month")["Amount"]
        .sum()
    )
    st.bar_chart(monthly_summary)
    # Pie Chart
    with left:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            fig1, ax1 = plt.subplots()
            ax1.pie(
                summary.values,
                labels=summary.index,
                autopct="%1.1f%%",
                startangle=90
            )
            ax1.axis("equal")
            st.pyplot(fig1)

            st.markdown('</div>', unsafe_allow_html=True)

    # Bar Chart
    with right:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            fig2, ax2 = plt.subplots()
            ax2.bar(summary.index, summary.values)
            plt.xticks(rotation=35)
            plt.title("Category Spending")
            st.pyplot(fig2)

            st.markdown('</div>', unsafe_allow_html=True)

    # Highest Spending Category
    top_category = summary.idxmax()
    top_amount = summary.max()

    st.success(
            f"Highest Spending Category: {top_category} (₹{top_amount:.2f})"
        )
        # Monthly Expense Trend

    st.markdown("## 📈 Expense Trend")
    trend_df = df.copy()

    trend_df["Date"] = pd.to_datetime(
        trend_df["Date"],
        format="%d-%m-%Y"
        )

    trend = trend_df.groupby("Date")["Amount"].sum()
    fig3, ax3 = plt.subplots(figsize=(8,4))
    ax3.plot(
            trend.index,
            trend.values,
            marker="o"
        )
    ax3.set_title("Expense Trend")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Amount (₹)")
    plt.xticks(rotation=45)
    st.pyplot(fig3)
        
    st.markdown("### 💡 Suggestions")

    if top_category == "Food":
            st.info("Try reducing restaurant expenses and cook more meals at home.")
    elif top_category == "Travel":
            st.info("Use public transport or plan grouped travel.")
    elif top_category == "Bills":
            st.info("Monitor electricity/mobile usage to reduce bills.")
    elif top_category == "Shopping":
            st.info("Avoid impulse buying. Purchase only planned items.")
    else:
            st.info("Set category budgets to improve savings.")

elif menu == "📋 Records":

    df = load_data()

    st.subheader("📋 All Expense Records")

    if len(df) == 0:
        st.warning("No records available.")

    else:

        # 🔍 Search
        search = st.text_input("🔍 Search Description")

        # 📂 Filter
        category = st.selectbox(
            "Filter by Category",
            ["All"] + list(df["Category"].unique())
        )

        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[
                filtered_df["Description"].str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if category != "All":
            filtered_df = filtered_df[
                filtered_df["Category"] == category
            ]

        # Show Records
        st.dataframe(filtered_df, use_container_width=True)

        # ==========================
        # ✏️ Edit Expense
        # ==========================

        st.markdown("## ✏️ Edit Expense")

        if len(filtered_df) > 0:

            edit_index = st.selectbox(
                "Select Expense to Edit",
                filtered_df.index,
                key="edit"
            )

            selected = filtered_df.loc[edit_index]

            new_date = st.date_input(
                "Date",
                value=datetime.strptime(
                    selected["Date"],
                    "%d-%m-%Y"
                )
            )

            categories = [
                "Food",
                "Travel",
                "Bills",
                "Shopping",
                "Health",
                "Entertainment",
                "Other"
            ]

            new_category = st.selectbox(
                "Category",
                categories,
                index=categories.index(selected["Category"])
            )

            new_amount = st.number_input(
                "Amount",
                value=float(selected["Amount"]),
                min_value=1.0
            )

            new_description = st.text_input(
                "Description",
                value=selected["Description"]
            )

            if st.button("Update Expense"):

                df.loc[edit_index, "Date"] = new_date.strftime("%d-%m-%Y")
                df.loc[edit_index, "Category"] = new_category
                df.loc[edit_index, "Amount"] = new_amount
                df.loc[edit_index, "Description"] = new_description

                save_data(df)

                st.success("Expense Updated Successfully!")

                st.rerun()

        # ==========================
        # 🗑 Delete Expense
        # ==========================

        st.markdown("## 🗑 Delete Expense")

        if len(filtered_df) > 0:

            delete_index = st.selectbox(
                "Select Expense to Delete",
                filtered_df.index,
                key="delete"
            )

            if st.button("Delete Selected Expense"):

                df = df.drop(delete_index).reset_index(drop=True)

                save_data(df)

                st.success("Expense Deleted Successfully!")

                st.rerun()

        # ==========================
        # 📥 Download CSV
        # ==========================

        csv = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download Expenses as CSV",
            data=csv,
            file_name="expenses_report.csv",
            mime="text/csv"
        )

        # ==========================
        # 🗑 Delete All Records
        # ==========================

        if st.button("Delete All Records"):

            os.remove(FILE_NAME)

            st.success("All data deleted successfully.")

            st.rerun()