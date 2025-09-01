import streamlit as st
import pandas as pd

st.set_page_config(page_title="Scanner", layout="wide")
st.title("📦 Scanning Table")

# -------------------
# Initialize session state
# -------------------
if "scans" not in st.session_state:
    st.session_state.scans = []
if "refocus_qr" not in st.session_state:
    st.session_state.refocus_qr = True  # focus QR on first load too

# -------------------
# Input form
# -------------------
with st.form("scan_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        qr_code = st.text_input("QR Code", key="qr_code")
    with col2:
        tracking_num = st.text_input("Tr # (Required)", key="tracking_num")
    with col3:
        imei = st.text_input("IMEI", key="imei")

    submitted = st.form_submit_button("➕ Add Scan")

# -------------------
# Save scan
# -------------------
if submitted:
    if not tracking_num:
        st.error("❌ Tracking # is required!")
    elif not qr_code or not imei:
        st.error("❌ All fields are required!")
    else:
        st.session_state.scans.append({
            "QR Code": qr_code,
            "Tr #": tracking_num,
            "IMEI": imei,
            "Status": False
        })
        st.success("✅ Scan added!")
        # tell next render to focus QR Code, then rerun immediately
        st.session_state.refocus_qr = True
        st.rerun()

# -------------------
# Table
# -------------------
if st.session_state.scans:
    df = pd.DataFrame(st.session_state.scans)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No scans yet. Start by adding your first scan above.")

# -------------------
# JS autofocus back to QR Code after submit/rerun
# -------------------
if st.session_state.refocus_qr:
    st.markdown(
        """
        <script>
        setTimeout(function () {
          // Find the text input whose aria-label equals the Streamlit label
          const el = document.querySelector('input[aria-label="QR Code"]');
          if (el) { el.focus(); el.select(); }
        }, 50);
        </script>
        """,
        unsafe_allow_html=True
    )
    st.session_state.refocus_qr = False
