import streamlit as st
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
import re
import time
from database_utils import init_db, add_contact, get_all_contacts, update_contact, delete_contact

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
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=80)
    st.title("MIRA Portal")
    if st.button(f"🌙 Switch Theme"):
        toggle_theme()
        st.rerun()
    st.markdown("---")
    menu = ["🌐 View Directory", "➕ Add New Contact", "✏️ Update Contact", "🗑️ Delete Contact"]
    choice = st.radio("Navigation Menu", menu)

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$', email)

def is_valid_phone(phone):
    return re.match(r'^\d+$', phone)

# --- VIEW ---
if choice == "🌐 View Directory":
    st.markdown("<div class='main-title'>🏥 MIRA Patient Directory</div>", unsafe_allow_html=True)
    contacts = get_all_contacts()
    st.write(f"Total Records: {len(contacts)}")
    for c in contacts:
        st.markdown(f'<div class="contact-card"><b>👤 {c["first_name"]} {c["last_name"]}</b><br>📩 {c["email"]} | 📞 {c["phone"]}<br>📍 {c["address"]}</div>', unsafe_allow_html=True)

# --- ADD ---
elif choice == "➕ Add New Contact":
    st.markdown("<div class='main-title'>➕ Register New Patient</div>", unsafe_allow_html=True)
    with st.form("add_form", clear_on_submit=True):
        fn = st.text_input("First Name")
        ln = st.text_input("Last Name")
        em = st.text_input("Email ID")
        ph = st.text_input("Phone Number")
        ad = st.text_area("Address")
        if st.form_submit_button("Save Record"):
            fn, ln, em, ph, ad = fn.strip(), ln.strip(), em.strip(), ph.strip(), ad.strip()
            if not (fn and ln and em and ph):
                st.error("All fields are mandatory.")
            elif not is_valid_email(em):
                st.error(f"Error: Invalid email format.")
            elif not is_valid_phone(ph):
                st.error(f"Error: Phone Number must contain digits only.")
            else:
                success, msg = add_contact(fn, ln, ad, em, ph)
                if success: st.success(msg)
                else: st.error(msg)

# --- UPDATE (CORRECTED) ---
elif choice == "✏️ Update Contact":
    st.markdown("<div class='main-title'>✏️ Edit Existing Record</div>", unsafe_allow_html=True)
    contacts = get_all_contacts()
    if contacts:
        options = [f"{c['id']} - {c['first_name']} {c['last_name']}" for c in contacts]
        selected = st.selectbox("Select patient to modify", options)
        cid = int(selected.split(" - ")[0])
        curr = next(c for c in contacts if c['id'] == cid)

        with st.form("edit_form"):
            u_fn = st.text_input("First Name", value=curr['first_name'])
            u_ln = st.text_input("Last Name", value=curr['last_name'])
            u_em = st.text_input("Email", value=curr['email'])
            u_ph = st.text_input("Phone", value=curr['phone'])
            u_ad = st.text_area("Address", value=curr['address'])
            
            if st.form_submit_button("Update All Information"):
                u_fn, u_ln, u_em, u_ph, u_ad = u_fn.strip(), u_ln.strip(), u_em.strip(), u_ph.strip(), u_ad.strip()
                
                if not (u_fn and u_ln and u_em and u_ph):
                    st.error("First Name, Last Name, Email, and Phone cannot be empty.")
                elif not is_valid_email(u_em):
                    st.error("Invalid email format.")
                elif not is_valid_phone(u_ph):
                    st.error("Phone must contain digits only.")
                else:
                    success, msg = update_contact(cid, u_fn, u_ln, u_ad, u_em, u_ph)
                    if success:
                        st.success("✅ Record updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
    else:
        st.info("No records to edit.")

# --- DELETE ---
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