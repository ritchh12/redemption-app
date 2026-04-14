


import streamlit as st
import mysql.connector
from datetime import datetime, timedelta



# 🔌 Database Connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mysql123",
        database="reward_app"
    )

st.title("💰 Code Redemption System")

# 🔐 SESSION STATE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# 📌 MENU
menu = st.sidebar.selectbox("Menu", ["Login", "Register"])

# 📝 REGISTER
if menu == "Register":
    st.subheader("Register")

    new_user = st.number_input("User ID", min_value=1, step=1)
    new_password = st.text_input("Password", type="password")

    if st.button("Register"):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = %s", (new_user,))
        if cursor.fetchone():
            st.error("User already exists")
        else:
            cursor.execute("""
            INSERT INTO users (id, password, balance)
            VALUES (%s, %s, %s)
            """, (new_user, new_password, 0))

            conn.commit()
            st.success("Account created successfully")

        conn.close()

# 🔑 LOGIN
elif menu == "Login":
    st.subheader("Login")

    user = st.number_input("User ID", min_value=1, step=1)
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT password FROM users WHERE id = %s", (user,))
        result = cursor.fetchone()

        if result:
            if result[0] == password:
                st.session_state.logged_in = True
                st.session_state.user_id = user
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Wrong password")
        else:
            st.error("User not found")

        conn.close()

# 🚫 STOP APP IF NOT LOGGED IN
if not st.session_state.logged_in:
    st.warning("Please login first")
    st.stop()

# 👤 CURRENT USER
user_id = st.session_state.user_id
st.success(f"Logged in as User: {user_id}")

# 🔓 LOGOUT
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.rerun()

# 🎯 CODE INPUT
code = st.text_input("Enter Code")

# 🎯 REDEEM BUTTON
if st.button("Redeem"):

    conn = get_connection()
    cursor = conn.cursor(buffered=True)

    # 🚫 BLOCK CHECK
    cursor.execute("""
    SELECT * FROM flagged_users 
    WHERE user_id = %s AND expires_at > NOW()
    """, (user_id,))
    
    if cursor.fetchone():
        st.error("🚫 Your account is temporarily blocked.")
        conn.close()
        st.stop()

    # ⚡ RATE LIMIT
    cursor.execute("""
    SELECT COUNT(*) FROM attempts 
    WHERE user_id = %s 
    AND attempt_time > NOW() - INTERVAL 1 MINUTE
    """, (user_id,))
    
    if cursor.fetchone()[0] > 20:
        st.error("Too many attempts")
        conn.close()
        st.stop()

    # 🔴 FAILED CHECK
    cursor.execute("""
    SELECT COUNT(*) FROM attempts 
    WHERE user_id = %s AND is_success = FALSE
    AND attempt_time > NOW() - INTERVAL 1 MINUTE
    """, (user_id,))
    
    failed = cursor.fetchone()[0]

    if failed > 10:
        st.warning("Suspicious activity")

        cursor.execute("""
        SELECT * FROM flagged_users 
        WHERE user_id = %s AND expires_at > NOW()
        """, (user_id,))

        if not cursor.fetchone():
            expiry = datetime.now() + timedelta(seconds=50)

            cursor.execute("""
            INSERT INTO flagged_users (user_id, expires_at)
            VALUES (%s, %s)
            """, (user_id, expiry))

        conn.commit()
        conn.close()
        st.stop()

    # 🔍 CHECK CODE
    cursor.execute("SELECT amount, is_used FROM codes WHERE BINARY code = %s", (code,))
    result = cursor.fetchone()

    if not result:
        st.error("Invalid Code")

        cursor.execute("""
        INSERT INTO attempts (code, is_success, user_id, reason)
        VALUES (%s, %s, %s, %s)
        """, (code, False, user_id, "INVALID"))

        conn.commit()

    else:
        amount, used = result

        if used:
            st.warning("Already used")

            cursor.execute("""
            INSERT INTO attempts (code, is_success, user_id, reason)
            VALUES (%s, %s, %s, %s)
            """, (code, False, user_id, "USED"))

            conn.commit()

        else:
            cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, user_id))
            cursor.execute("UPDATE codes SET is_used = TRUE WHERE BINARY code = %s", (code,))
            cursor.execute("INSERT INTO transactions (user_id, code, amount) VALUES (%s, %s, %s)", (user_id, code, amount))

            cursor.execute("""
            INSERT INTO attempts (code, is_success, user_id, reason)
            VALUES (%s, %s, %s, %s)
            """, (code, True, user_id, "SUCCESS"))

            conn.commit()
            st.success(f"₹{amount} added!")

    conn.close()

# 💳 BALANCE
if st.button("Check Balance"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
    st.info(f"Balance: ₹{cursor.fetchone()[0]}")
    conn.close()

# 📊 TRANSACTIONS
if st.button("Show Transactions"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions ORDER BY timestamp DESC")
    st.table(cursor.fetchall())
    conn.close()