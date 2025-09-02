import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

st.set_page_config(page_title="Scanner App", layout="wide")

# -------------------
# 🔑 ShipStation Credentials (replace with your actual keys)
# -------------------
SHIPSTATION_API_KEY = st.secrets["SHIPSTATION_API_KEY"]
SHIPSTATION_API_SECRET = st.secrets["SHIPSTATION_API_SECRET"]

# -------------------
# Session State Initialization
# -------------------
if "page" not in st.session_state:
    st.session_state.page = "home"  # default page
if "scans_scan2" not in st.session_state:
    st.session_state.scans_scan2 = []
if "scans_scan1" not in st.session_state:
    st.session_state.scans_scan1 = []
if "refocus_qr" not in st.session_state:
    st.session_state.refocus_qr = False

# -------------------
# ShipStation verification helper
# -------------------
def verify_with_shipstation(tracking_num, imei):
    try:
        url = f"https://ssapi.shipstation.com/shipments?trackingNumber={tracking_num}"
        response = requests.get(url, auth=HTTPBasicAuth(SHIPSTATION_API_KEY, SHIPSTATION_API_SECRET))

        if response.status_code != 200:
            return False, f"API Error {response.status_code}"

        data = response.json()
        if not data.get("shipments"):
            return False, "No shipment found"

        shipment = data["shipments"][0]
        order_id = shipment.get("orderId")

        if not order_id:
            return False, "No orderId found in shipment"

        # Fetch order details
        order_url = f"https://ssapi.shipstation.com/orders/{order_id}"
        order_resp = requests.get(order_url, auth=HTTPBasicAuth(SHIPSTATION_API_KEY, SHIPSTATION_API_SECRET))

        if order_resp.status_code != 200:
            return False, "Order lookup failed"

        order_data = order_resp.json()

        # Check if IMEI exists in any item SKU
        for item in order_data.get("items", []):
            if imei in (item.get("sku") or ""):
                return True, "Match found ✅"

        return False, "IMEI not found in order items ❌"

    except Exception as e:
        return False, f"Exception: {str(e)}"

# -------------------
# Navigation Buttons
# -------------------
col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 6])
with col_nav1:
    if st.button("🏠 Home"):
        st.session_state.page = "home"
        st.rerun()
with col_nav2:
    if st.button("🎯 Scan 1"):
        st.session_state.page = "scan1"
        st.rerun()
with col_nav3:
    if st.button("📦 Scan 2"):
        st.session_state.page = "scan2"
        st.rerun()

st.markdown("---")

# -------------------
# Page: Home
# -------------------
if st.session_state.page == "home":
    st.title("🏠 Home")
    st.info("Welcome to the Scanner App. Use the buttons above to start scanning.")

# -------------------
# Page: Scan 1 (validation logic unchanged)
# -------------------
elif st.session_state.page == "scan1":
    st.title("🎯 Scan 1 Table")

    def check_duplicate_ic(field_name, value):
        if not value:
            return False
        for row in st.session_state.scans_scan1:
            if row[field_name] == value:
                return True
        return False

    with st.form("scan1_form", clear_on_submit=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            qr_code = st.text_input("QR Code", key="qr_code_scan1")
        with col2:
            black_ic = st.text_input("black_ic", key="black_ic_scan1")
        with col3:
            blue_ic = st.text_input("blue_ic", key="blue_ic_scan1")
        with col4:
            u_blue_ic = st.text_input("u_blue_ic", key="u_blue_ic_scan1")
        with col5:
            red_ic = st.text_input("red_ic", key="red_ic_scan1")

        submitted = st.form_submit_button("➕ Add Scan (Scan 1)")

    if submitted:
        if not qr_code:
            st.error("❌ QR Code is required!")
        elif any(row["QR Code"] == qr_code for row in st.session_state.scans_scan1):
            st.error("❌ Duplicate QR Code")
        elif black_ic and (
            check_duplicate_ic("black_ic", black_ic)
            or not (len(black_ic) == 20 and black_ic.startswith("6641"))
        ):
            st.error("❌ Check for duplicate ic or incorrect ic value for black_ic")
        elif blue_ic and (
            check_duplicate_ic("blue_ic", blue_ic)
            or not (len(blue_ic) == 19 and blue_ic.startswith("6601"))
        ):
            st.error("❌ Check for duplicate ic or incorrect ic value for blue_ic")
        elif u_blue_ic and (
            check_duplicate_ic("u_blue_ic", u_blue_ic)
            or not (len(u_blue_ic) == 19 and u_blue_ic.startswith("6601"))
        ):
            st.error("❌ Check for duplicate ic or incorrect ic value for u_blue_ic")
        elif red_ic and (
            check_duplicate_ic("red_ic", red_ic)
            or not (len(red_ic) == 20 and red_ic.startswith("6601"))
        ):
            st.error("❌ Check for duplicate ic or incorrect ic value for red_ic")
        else:
            st.session_state.scans_scan1.append({
                "QR Code": qr_code,
                "black_ic": black_ic,
                "blue_ic": blue_ic,
                "u_blue_ic": u_blue_ic,
                "red_ic": red_ic,
                "Status": False
            })
            st.success("✅ Scan added to Scan 1!")

    if st.session_state.scans_scan1:
        df1 = pd.DataFrame(st.session_state.scans_scan1)
        st.dataframe(df1, use_container_width=True)
    else:
        st.info("No scans yet in Scan 1. Start scanning above.")

# -------------------
# Page: Scan 2 (with ShipStation API integration)
# -------------------
elif st.session_state.page == "scan2":
    st.title("📦 Scan 2 Table")

    with st.form("scan2_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            qr_code = st.text_input("QR Code (Scan 2)", key="qr_code_scan2")
        with col2:
            tracking_num = st.text_input("Tr # (Required)", key="tracking_num_scan2")
        with col3:
            imei = st.text_input("IMEI", key="imei_scan2")

        submitted = st.form_submit_button("➕ Add Scan (Scan 2)")

    if submitted:
        if not tracking_num:
            st.error("❌ Tracking # is required!")
        elif not qr_code or not imei:
            st.error("❌ All fields are required!")
        else:
            status, msg = verify_with_shipstation(tracking_num, imei)

            st.session_state.scans_scan2.append({
                "QR Code": qr_code,
                "Tr #": tracking_num,
                "IMEI": imei,
                "Status": status
            })

            if status:
                st.success(f"✅ Verified: {msg}")
            else:
                st.error(f"❌ Verification failed: {msg}")

            st.session_state.refocus_qr = True
            st.rerun()

    if st.session_state.scans_scan2:
        df2 = pd.DataFrame(st.session_state.scans_scan2)
        st.dataframe(df2, use_container_width=True)
    else:
        st.info("No scans yet in Scan 2. Start scanning above.")

# -------------------
# Autofocus JS
# -------------------
if st.session_state.refocus_qr:
    st.markdown(
        """
        <script>
        setTimeout(function () {
          const el = document.querySelector('input[aria-label^="QR Code"]');
          if (el) { el.focus(); el.select(); }
        }, 50);
        </script>
        """,
        unsafe_allow_html=True
    )
    st.session_state.refocus_qr = False
