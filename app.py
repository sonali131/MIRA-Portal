import streamlit as st
import re
import time  # मैसेज दिखाने के लिए समय देने हेतु
from database_utils import init_db, add_contact, get_all_contacts, update_contact, delete_contact

# 1. Configuration
st.set_page_config(page_title="MIRA | Patient Management", page_icon="🏥", layout="wide")

# 2. THEME LOGIC For Light And Dark Mode
if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

def toggle_theme():
    st.session_state.theme = 'Dark' if st.session_state.theme == 'Light' else 'Light'

# 3. CUSTOM CSS 
light_css = """
<style>
    .main { background-color: #f8f9fa; color: #212529; }
    .contact-card { background-color: white; border: 1px solid #dee2e6; color: #212529; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #007bff; }
    .main-title { color: #007bff; font-weight: bold; text-align: center; font-size: 35px; margin-bottom: 20px; }
</style>
"""

dark_css = """
<style>
    .main { background-color: #0e1117; color: white; }
    .contact-card { background-color: #262730; border: 1px solid #464855; color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00d4ff; }
    .main-title { color: #00d4ff; font-weight: bold; text-align: center; font-size: 35px; margin-bottom: 20px; }
</style>
"""

st.markdown(dark_css if st.session_state.theme == 'Dark' else light_css, unsafe_allow_html=True)

# Initialize Database
init_db()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=80)
    st.title("MIRA Portal")
    
    if st.button(f"🌙 Switch to { 'Light' if st.session_state.theme == 'Dark' else 'Dark' } Mode"):
        toggle_theme()
        st.rerun()
    
    st.markdown("---")
    menu = ["🌐 View Directory", "➕ Add New Contact", "✏️ Update Contact", "🗑️ Delete Contact"]
    choice = st.radio("Navigation Menu", menu)
    st.markdown("---")
    st.write("Logged in as: **Admin User**")

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

# --- PAGE LOGIC ---

# 1. VIEW SECTION
if choice == "🌐 View Directory":
    st.markdown("<div class='main-title'>🏥 MIRA Patient Directory</div>", unsafe_allow_html=True)
    contacts = get_all_contacts()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Records", len(contacts))
    c2.metric("Database Status", "Active")
    c3.metric("Platform", "MIRA Core")

    search_query = st.text_input("🔍 Search Patients", placeholder="Enter name or email...")

    if contacts:
        for c in contacts:
            if search_query.lower() in c['first_name'].lower() or search_query.lower() in c['email'].lower():
                st.markdown(f"""
                    <div class="contact-card">
                        <b>👤 {c['first_name']} {c['last_name']}</b> (ID: #{c['id']})<br>
                        <div style="font-size:14px; margin-top:5px;">
                            📩 {c['email']} | 📞 {c['phone']}<br>
                            📍 {c['address']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("The directory is currently empty.")

# 2. ADD SECTION
elif choice == "➕ Add New Contact":
    st.markdown("<div class='main-title'>➕ Register New Patient</div>", unsafe_allow_html=True)
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        fname = col1.text_input("First Name")
        lname = col2.text_input("Last Name")
        email = st.text_input("Email ID")
        phone = st.text_input("Phone Number")
        addr = st.text_area("Address")
        
        if st.form_submit_button("Save Record"):
            if not (fname and lname and email and phone):
                st.error("Please fill all required fields.")
            elif not is_valid_email(email):
                st.warning("Invalid email format.")
            else:
                success, msg = add_contact(fname, lname, addr, email, phone)
                if success:
                    st.success(f"✅ Success: {fname} {lname} added to database.")
                else:
                    st.error(msg)

# 3. UPDATE SECTION
elif choice == "✏️ Update Contact":
    st.markdown("<div class='main-title'>✏️ Edit Existing Record</div>", unsafe_allow_html=True)
    contacts = get_all_contacts()
    
    if not contacts:
        st.info("No records available to update.")
    else:
        options = [f"{c['id']} - {c['first_name']} {c['last_name']}" for c in contacts]
        selected = st.selectbox("Select patient to edit", options)
        cid = int(selected.split(" - ")[0])
        curr = next(c for c in contacts if c['id'] == cid)

        with st.form("edit_form"):
            u_fn = st.text_input("First Name", value=curr['first_name'])
            u_ln = st.text_input("Last Name", value=curr['last_name'])
            u_email = st.text_input("Email", value=curr['email'])
            u_phone = st.text_input("Phone", value=curr['phone'])
            u_addr = st.text_area("Address", value=curr['address'])
            
            if st.form_submit_button("Update Information"):
                update_contact(cid, u_fn, u_ln, u_addr, u_email, u_phone)
                st.success("✅ Database updated successfully!")
                time.sleep(1.5) # 1.5 सेकंड का इंतज़ार ताकि यूज़र मैसेज देख सके
                st.rerun()

# 4. DELETE SECTION
elif choice == "🗑️ Delete Contact":
    st.markdown("<div class='main-title'>🗑️ Remove Record</div>", unsafe_allow_html=True)
    contacts = get_all_contacts()
    
    if not contacts:
        st.info("No records available to delete.")
    else:
        options = [f"{c['id']} - {c['first_name']} {c['last_name']}" for c in contacts]
        selected = st.selectbox("Select patient to permanently remove", options)
        cid = int(selected.split(" - ")[0])
        
        st.warning(f"Are you sure you want to delete record ID #{cid}?")
        if st.button("Confirm Permanent Deletion"):
            delete_contact(cid)
            st.success("🗑️ Record deleted successfully!")
            time.sleep(1.5) 
            st.rerun()