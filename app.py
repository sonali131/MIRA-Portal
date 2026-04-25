import streamlit as st
import re
import time
from database_utils import init_db, add_contact, get_all_contacts, update_contact, delete_contact

# FIXED: Removed the Emoji from page_icon to prevent MemoryError
st.set_page_config(page_title="MIRA | Patient Management", page_icon="M", layout="wide")

if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

def toggle_theme():
    st.session_state.theme = 'Dark' if st.session_state.theme == 'Light' else 'Light'

light_css = """<style>.main { background-color: #f8f9fa; color: #212529; } .contact-card { background-color: white; border: 1px solid #dee2e6; color: #212529; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #007bff; } .main-title { color: #007bff; font-weight: bold; text-align: center; font-size: 35px; margin-bottom: 20px; }</style>"""
dark_css = """<style>.main { background-color: #0e1117; color: white; } .contact-card { background-color: #262730; border: 1px solid #464855; color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00d4ff; } .main-title { color: #00d4ff; font-weight: bold; text-align: center; font-size: 35px; margin-bottom: 20px; }</style>"""

st.markdown(dark_css if st.session_state.theme == 'Dark' else light_css, unsafe_allow_html=True)
init_db()

with st.sidebar:
    # Sidebar 
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=80)
    st.title("MIRA Portal")
    if st.button(f"🌙 Switch Theme"):
        toggle_theme()
        st.rerun()
    st.markdown("---")
    menu = ["🌐 View Directory", "➕ Add New Contact", "✏️ Update Contact", "🗑️ Delete Contact"]
    choice = st.radio("Navigation Menu", menu)

def is_valid_email(email):
    # Task 2  Regex Which chekcs .com / .in 
    return re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email)

def is_valid_phone(phone):
    # Jason Larry  'A' Check A character
    return re.match(r'^\d+$', phone)

if choice == "🌐 View Directory":
    st.markdown("<div class='main-title'>🏥 MIRA Patient Directory</div>", unsafe_allow_html=True)
    contacts = get_all_contacts()
    st.write(f"Total Records: {len(contacts)}")
    for c in contacts:
        st.markdown(f'<div class="contact-card"><b>👤 {c["first_name"]} {c["last_name"]}</b><br>📩 {c["email"]} | 📞 {c["phone"]}<br>📍 {c["address"]}</div>', unsafe_allow_html=True)

elif choice == "➕ Add New Contact":
    st.markdown("<div class='main-title'>➕ Register New Patient</div>", unsafe_allow_html=True)
    with st.form("add_form", clear_on_submit=True):
        fn = st.text_input("First Name")
        ln = st.text_input("Last Name")
        em = st.text_input("Email ID")
        ph = st.text_input("Phone Number")
        ad = st.text_area("Address")
        
        if st.form_submit_button("Save Record"):
            # .strip() remove space
            fn_clean = fn.strip()
            ln_clean = ln.strip()
            em_clean = em.strip()
            ph_clean = ph.strip()
            ad_clean = ad.strip()

            if not (fn_clean and ln_clean and em_clean and ph_clean):
                st.error("All fields are mandatory.")
            elif not is_valid_email(em_clean):
                st.error(f"Error: '{em_clean}' is an invalid email format.")
            elif not is_valid_phone(ph_clean):
                st.error(f"Error: Phone Number '{ph_clean}' must contain digits only.")
            else:
                success, msg = add_contact(fn_clean, ln_clean, ad_clean, em_clean, ph_clean)
                if success: st.success(msg)
                else: st.error(msg)

elif choice == "✏️ Update Contact":
    st.markdown("<div class='main-title'>✏️ Edit Record</div>", unsafe_allow_html=True)
    contacts = get_all_contacts()
    if contacts:
        options = [f"{c['id']} - {c['first_name']} {c['last_name']}" for c in contacts]
        selected = st.selectbox("Select patient", options)
        cid = int(selected.split(" - ")[0])
        curr = next(c for c in contacts if c['id'] == cid)
        with st.form("edit"):
            u_em = st.text_input("New Email", value=curr['email'])
            if st.form_submit_button("Update Email"):
                update_contact(cid, curr['first_name'], curr['last_name'], curr['address'], u_em, curr['phone'])
                st.success("✅ Email Updated!")
                time.sleep(1)
                st.rerun()

elif choice == "🗑️ Delete Contact":
    st.markdown("<div class='main-title'>🗑️ Remove Record</div>", unsafe_allow_html=True)
    contacts = get_all_contacts()
    if contacts:
        options = [f"{c['id']} - {c['first_name']} {c['last_name']}" for c in contacts]
        selected = st.selectbox("Select patient to remove", options)
        cid = int(selected.split(" - ")[0])
        if st.button("Confirm Delete"):
            delete_contact(cid)
            st.success("🗑️ Record Deleted!")
            time.sleep(1)
            st.rerun()