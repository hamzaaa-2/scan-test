import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

st.set_page_config(page_title="Scanner App", layout="wide")

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

# ============================================================
# PAGE: HOME
# ============================================================
if st.session_state.page == "home":
    st.title("🏠 Home")
    st.info("Welcome to the Scanner App. Use the buttons above to start scanning.")


# ============================================================
# PAGE: SCAN 1
# (5-column table with IC validation)
# ============================================================
elif st.session_state.page == "scan1":
    st.title("🎯 Scan 1 Table")

    # Helper function to check duplicate IC values
    def check_duplicate_ic(field_name, value):
        if not value:  # empty values are allowed
            return False
        for row in st.session_state.scans_scan1:
            if row[field_name] == value:
                return True
        return False

    # Input form
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

    # Validation + Save
    if submitted:
        # QR Code is mandatory
        if not qr_code:
            st.error("❌ QR Code is required!")
        elif any(row["QR Code"] == qr_code for row in st.session_state.scans_scan1):
            st.error("❌ Duplicate QR Code")

        # black_ic validation (if provided)
        elif black_ic and (
            check_duplicate_ic("black_ic", black_ic)
            or not (len(black_ic) == 20 and black_ic.startswith("6641"))
        ):
            st.error("❌ Check for duplicate ic or incorrect ic value for black_ic")

        # blue_ic validation (if provided)
        elif blue_ic and (
            check_duplicate_ic("blue_ic", blue_ic)
            or not (len(blue_ic) == 19 and blue_ic.startswith("6601"))
        ):
            st.error("❌ Check for duplicate ic or incorrect ic value for blue_ic")

        # u_blue_ic validation (if provided)
        elif u_blue_ic and (
            check_duplicate_ic("u_blue_ic", u_blue_ic)
            or not (len(u_blue_ic) == 19 and u_blue_ic.startswith("6601"))
        ):
            st.error("❌ Check for duplicate ic or incorrect ic value for u_blue_ic")

        # red_ic validation (if provided)
        elif red_ic and (
            check_duplicate_ic("red_ic", red_ic)
            or not (len(red_ic) == 20 and red_ic.startswith("6601"))
        ):
            st.error("❌ Check for duplicate ic or incorrect ic value for red_ic")

        else:
            # ✅ Passed all checks → save row
            st.session_state.scans_scan1.append({
                "QR Code": qr_code,
                "black_ic": black_ic,
                "blue_ic": blue_ic,
                "u_blue_ic": u_blue_ic,
                "red_ic": red_ic,
                "Status": False
            })
            st.success("✅ Scan added to Scan 1!")

    # Display table
    if st.session_state.scans_scan1:
        df1 = pd.DataFrame(st.session_state.scans_scan1)
        st.dataframe(df1, use_container_width=True)
    else:
        st.info("No scans yet in Scan 1. Start scanning above.")


# ============================================================
# PAGE: SCAN 2
# (SKU logic + optional IMEI as DE-001 item)
# ============================================================
elif st.session_state.page == "scan2":
    st.title("📦 Scan 2 Table")

    # --- Helper: Determine SKU from QR Code ---
    def get_sku_from_qr(qr_code: str):
        if len(qr_code) == 4 and qr_code.isdigit():
            return "SK-001"  # SK logic
        elif len(qr_code) == 20 and qr_code.startswith("6641"):
            return "IC-001"  # Black IC logic
        elif len(qr_code) == 19 and qr_code.startswith("6601"):
            return "IC-002"  # Blue IC logic
        elif len(qr_code) == 20 and qr_code.startswith("6601"):
            return "IC-004"  # Red IC logic
        return None

    # --- Helper: Verify SKU against ShipStation ---
    def verify_with_shipstation(tracking_num: str, sku: str):
        api_key = st.secrets["SHIPSTATION_API_KEY"]
        api_secret = st.secrets["SHIPSTATION_API_SECRET"]

        if not api_key or not api_secret:
            st.warning("⚠️ ShipStation API credentials not set in environment.")
            return False

        try:
            resp = requests.get(
                f"https://ssapi.shipstation.com/shipments?trackingNumber={tracking_num}",
                auth=(api_key, api_secret)
            )
            if resp.status_code != 200:
                st.error(f"❌ API error: {resp.status_code}")
                return False

            data = resp.json()
            shipments = data.get("shipments", [])
            if not shipments:
                st.warning("⚠️ No shipment found for this tracking number.")
                return False

            # Collect SKUs from order items
            order_items = []
            for shipment in shipments:
                for item in shipment.get("shipmentItems", []):
                    order_items.append(item.get("sku"))

            return sku in order_items

        except Exception as e:
            st.error(f"❌ API exception: {e}")
            return False

    # Input form
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
        elif not qr_code:
            st.error("❌ QR Code is required!")
        else:
            rows_to_add = []

            # Always add the QR Code item
            sku = get_sku_from_qr(qr_code)
            if sku:
                verified = verify_with_shipstation(tracking_num, sku)
                rows_to_add.append({
                    "QR Code": qr_code,
                    "Tr #": tracking_num,
                    "IMEI": "",
                    "SKU": sku,
                    "Status": verified  # ✅ or ❌ depending on API check
                })
            else:
                st.warning("⚠️ QR Code does not match any SKU rule.")

            # If IMEI provided and valid, add it as DE-001
            if imei and len(imei) == 15 and imei.isdigit():
                verified = verify_with_shipstation(tracking_num, "DE-001")
                rows_to_add.append({
                    "QR Code": "",
                    "Tr #": tracking_num,
                    "IMEI": imei,
                    "SKU": "DE-001",
                    "Status": verified
                })

            if rows_to_add:
                st.session_state.scans_scan2.extend(rows_to_add)
                st.success("✅ Scan(s) added to Scan 2!")

            # Refocus QR field
            st.session_state.refocus_qr = True
            st.rerun()

    # Display table
    if st.session_state.scans_scan2:
        df2 = pd.DataFrame(st.session_state.scans_scan2)
        st.dataframe(df2, use_container_width=True)
    else:
        st.info("No scans yet in Scan 2. Start scanning above.")

# ============================================================
# Autofocus JS (for Scan 2 QR Code input)
# ============================================================
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
