import streamlit as st
import re
from database_utils import init_db, add_contact, get_all_contacts, update_contact, delete_contact

# 1. Configration
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
    .main-title { color: #007bff; font-weight: bold; text-align: center; font-size: 35px; }
</style>
"""

dark_css = """
<style>
    .main { background-color: #0e1117; color: white; }
    .contact-card { background-color: #262730; border: 1px solid #464855; color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00d4ff; }
    .main-title { color: #00d4ff; font-weight: bold; text-align: center; font-size: 35px; }
</style>
"""

# Theme
st.markdown(dark_css if st.session_state.theme == 'Dark' else light_css, unsafe_allow_html=True)

# Start/initilazation of database
init_db()

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=80)
    st.title("MIRA Portal")
    
    # THEME TOGGLE BUTTON
    st.markdown("---")
    if st.button(f"🌙 Switch to { 'Light' if st.session_state.theme == 'Dark' else 'Dark' } Mode"):
        toggle_theme()
        st.rerun()
    
    st.markdown("---")
    menu = ["🌐 View Directory", "➕ New Registration", "⚙️ Database Tools"]
    choice = st.radio("Navigation Menu", menu)
    st.markdown("---")
    st.write("Logged in as: **Admin User**")

# --- MAIN LOGIC ---

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

if choice == "🌐 View Directory":
    st.markdown("<div class='main-title'>🏥 MIRA Patient Directory</div>", unsafe_allow_html=True)
    
    contacts = get_all_contacts()
    
    #Dashboard
    c1, c2, c3 = st.columns(3)
    c1.metric("Registered Patients", len(contacts))
    c2.metric("Server Status", "Online")
    c3.metric("Data Sync", "Local SQL")

    st.markdown("### 🔍 Search & Filter")
    search_query = st.text_input("", placeholder="Type name or email to search...")

    if contacts:
        for c in contacts:
            if search_query.lower() in c['first_name'].lower() or search_query.lower() in c['email'].lower():
                st.markdown(f"""
                    <div class="contact-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-size:18px;"><b>👤 {c['first_name']} {c['last_name']}</b></span>
                            <span style="color:gray; font-size:12px;">ID: #{c['id']}</span>
                        </div>
                        <div style="margin-top:8px; font-size:14px;">
                            📩 {c['email']} | 📞 {c['phone']}<br>
                            📍 {c['address']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No records found. Use the 'New Registration' tab to add patients.")

elif choice == "➕ New Registration":
    st.markdown("<div class='main-title'>➕ Patient Onboarding</div>", unsafe_allow_html=True)
    
    with st.container():
        with st.form("reg_form", clear_on_submit=True):
            st.write("Please fill in the medical contact details below:")
            col1, col2 = st.columns(2)
            fname = col1.text_input("First Name", placeholder="Enter first name")
            lname = col2.text_input("Last Name", placeholder="Enter last name")
            
            email = st.text_input("Official Email ID", placeholder="example@clinic.com")
            phone = st.text_input("Phone Number", placeholder="+91 XXX-XXX-XXXX")
            
            addr = st.text_area("Residential Address", placeholder="Street, City, State...")
            
            submitted = st.form_submit_button("✅ Register Patient")
            
            if submitted:
                if not (fname and lname and email and phone):
                    st.error("Missing required fields (*)")
                elif not is_valid_email(email):
                    st.warning("Invalid email format.")
                else:
                    success, msg = add_contact(fname, lname, addr, email, phone)
                    if success:
                        st.success(f"Record for {fname} has been safely encrypted and saved.")
                        st.balloons()
                    else:
                        st.error(msg)

elif choice == "⚙️ Database Tools":
    st.markdown("<div class='main-title'>⚙️ Record Management</div>", unsafe_allow_html=True)
    
    contacts = get_all_contacts()
    if contacts:
        options = [f"{c['id']} - {c['first_name']} {c['last_name']}" for c in contacts]
        selected_option = st.selectbox("Select patient to modify", options)
        cid = int(selected_option.split(" - ")[0])
        curr = next(c for c in contacts if c['id'] == cid)

        col_a, col_b = st.columns([2, 1])

        with col_a:
            st.markdown("#### ✏️ Edit Profile")
            with st.form("edit_form"):
                u_fn = st.text_input("First Name", value=curr['first_name'])
                u_ln = st.text_input("Last Name", value=curr['last_name'])
                u_email = st.text_input("Email", value=curr['email'])
                u_phone = st.text_input("Phone", value=curr['phone'])
                u_addr = st.text_area("Address", value=curr['address'])
                
                if st.form_submit_button("Update Records"):
                    update_contact(cid, u_fn, u_ln, u_addr, u_email, u_phone)
                    st.toast("Success: Database updated.")
                    st.rerun()

        with col_b:
            st.markdown("#### 🗑️ Deletion")
            st.warning("Once deleted, medical records cannot be recovered.")
            if st.button("Confirm Deletion", type="secondary"):
                delete_contact(cid)
                st.toast("Record deleted.")
                st.rerun()