import streamlit as st
import pandas as pd

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

# -------------------
# Page: Home (blank)
# -------------------
if st.session_state.page == "home":
    st.title("🏠 Home")
    st.info("Welcome to the Scanner App. Use the buttons above to start scanning.")

# -------------------
# Page: Scan 1 (5-column table)
# -------------------
elif st.session_state.page == "scan1":
    st.title("🎯 Scan 1 Table")

    with st.form("scan1_form", clear_on_submit=True):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            qr_code = st.text_input("QR Code (Scan 1)", key="qr_code_scan1")
        with col2:
            black_ic = st.text_input("black_ic", key="black_ic")
        with col3:
            blue_ic = st.text_input("blue_ic", key="blue_ic")
        with col4:
            u_blue_ic = st.text_input("u_blue_ic", key="u_blue_ic")
        with col5:
            red_ic = st.text_input("red_ic", key="red_ic")

        submitted = st.form_submit_button("➕ Add Scan (Scan 1)")

    if submitted:
        if not qr_code or not black_ic or not blue_ic or not u_blue_ic or not red_ic:
            st.error("❌ All fields are required!")
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
            st.session_state.refocus_qr = True
            st.rerun()

    if st.session_state.scans_scan1:
        df1 = pd.DataFrame(st.session_state.scans_scan1)
        st.dataframe(df1, use_container_width=True)
    else:
        st.info("No scans yet in Scan 1. Start scanning above.")

# -------------------
# Page: Scan 2 (3-column table — old home)
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
            st.session_state.scans_scan2.append({
                "QR Code": qr_code,
                "Tr #": tracking_num,
                "IMEI": imei,
                "Status": False
            })
            st.success("✅ Scan added to Scan 2!")
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
          // Find the first input with 'QR Code' in its label and focus
          const el = document.querySelector('input[aria-label^="QR Code"]');
          if (el) { el.focus(); el.select(); }
        }, 50);
        </script>
        """,
        unsafe_allow_html=True
    )
    st.session_state.refocus_qr = False
