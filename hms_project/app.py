import streamlit as st
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from core.models import Specialty
from patient_app.models import Patient
from doctor_app.models import Doctor, Appointment, MedicalRecord
from datetime import date, time

# Page config
st.set_page_config(page_title="Hospital Management System", page_icon="🏥", layout="wide")

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def login_page():
    st.title("🏥 Hospital Management System")
    
    tab1, tab2, tab3 = st.tabs(["Admin Login", "Doctor Login", "Patient Login/Register"])
    
    with tab1:
        st.subheader("Admin Login")
        username = st.text_input("Username", key="admin_user")
        password = st.text_input("Password", type="password", key="admin_pass")
        if st.button("Login as Admin"):
            user = authenticate(username=username, password=password)
            if user and user.is_superuser:
                st.session_state.logged_in = True
                st.session_state.user_type = "admin"
                st.session_state.user_id = user.id
                st.rerun()
            else:
                st.error("Invalid admin credentials")
    
    with tab2:
        st.subheader("Doctor Login")
        email = st.text_input("Email", key="doc_email")
        password = st.text_input("Password", type="password", key="doc_pass")
        if st.button("Login as Doctor"):
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    doctor = Doctor.objects.get(user=user)
                    st.session_state.logged_in = True
                    st.session_state.user_type = "doctor"
                    st.session_state.user_id = doctor.id
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            except:
                st.error("Doctor not found")
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Patient Login")
            email = st.text_input("Email", key="pat_email")
            password = st.text_input("Password", type="password", key="pat_pass")
            if st.button("Login as Patient"):
                try:
                    user = User.objects.get(email=email)
                    if user.check_password(password):
                        patient = Patient.objects.get(user=user)
                        st.session_state.logged_in = True
                        st.session_state.user_type = "patient"
                        st.session_state.user_id = patient.id
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except:
                    st.error("Patient not found")
        
        with col2:
            st.subheader("Patient Registration")
            with st.form("register_form"):
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                age = st.number_input("Age", min_value=1, max_value=120)
                gender = st.selectbox("Gender", ["M", "F", "O"])
                contact = st.text_input("Contact")
                address = st.text_area("Address")
                dob = st.date_input("Date of Birth")
                
                if st.form_submit_button("Register"):
                    try:
                        user = User.objects.create_user(
                            username=email,
                            email=email,
                            password=password,
                            first_name=first_name,
                            last_name=last_name
                        )
                        Patient.objects.create(
                            user=user,
                            age=age,
                            gender=gender,
                            contact=contact,
                            address=address,
                            date_of_birth=dob
                        )
                        st.success("Registration successful! Please login.")
                    except:
                        st.error("Registration failed. Email may already exist.")

def admin_dashboard():
    st.title("Admin Dashboard")
    
    menu = st.sidebar.selectbox("Menu", ["Dashboard", "Patients", "Doctors", "Appointments", "Specialties"])
    
    if menu == "Dashboard":
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Patients", Patient.objects.count())
        col2.metric("Total Doctors", Doctor.objects.count())
        col3.metric("Total Appointments", Appointment.objects.count())
        col4.metric("Specialties", Specialty.objects.count())
    
    elif menu == "Patients":
        st.subheader("All Patients")
        patients = Patient.objects.all()
        for p in patients:
            st.write(f"**{p.user.first_name} {p.user.last_name}** - Age: {p.age}, Gender: {p.gender}, Contact: {p.contact}")
    
    elif menu == "Doctors":
        st.subheader("All Doctors")
        doctors = Doctor.objects.all()
        for d in doctors:
            st.write(f"**Dr. {d.user.first_name} {d.user.last_name}** - Specialty: {d.specialty.name}, Contact: {d.contact}")
        
        st.subheader("Add New Doctor")
        with st.form("add_doctor"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            specialty = st.selectbox("Specialty", [s.name for s in Specialty.objects.all()])
            contact = st.text_input("Contact")
            
            if st.form_submit_button("Add Doctor"):
                try:
                    user = User.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)
                    spec = Specialty.objects.get(name=specialty)
                    Doctor.objects.create(user=user, specialty=spec, contact=contact)
                    st.success("Doctor added successfully!")
                    st.rerun()
                except:
                    st.error("Failed to add doctor")
    
    elif menu == "Appointments":
        st.subheader("All Appointments")
        appointments = Appointment.objects.all()
        for a in appointments:
            st.write(f"**{a.patient}** with **{a.doctor}** on {a.date} at {a.time} - Status: {a.status}")
    
    elif menu == "Specialties":
        st.subheader("Medical Specialties")
        specialties = Specialty.objects.all()
        for s in specialties:
            st.write(f"- {s.name}")

def doctor_dashboard():
    st.title("Doctor Dashboard")
    doctor = Doctor.objects.get(id=st.session_state.user_id)
    st.write(f"Welcome, Dr. {doctor.user.first_name} {doctor.user.last_name}")
    
    menu = st.sidebar.selectbox("Menu", ["My Appointments", "Add Medical Record"])
    
    if menu == "My Appointments":
        st.subheader("My Appointments")
        appointments = Appointment.objects.filter(doctor=doctor)
        for a in appointments:
            st.write(f"**{a.patient}** on {a.date} at {a.time} - Status: {a.status}")
    
    elif menu == "Add Medical Record":
        st.subheader("Add Medical Record")
        patients = Patient.objects.all()
        patient_names = [f"{p.user.first_name} {p.user.last_name}" for p in patients]
        
        with st.form("add_record"):
            patient_name = st.selectbox("Patient", patient_names)
            diagnosis = st.text_area("Diagnosis")
            treatment = st.text_area("Treatment")
            
            if st.form_submit_button("Add Record"):
                patient = patients[patient_names.index(patient_name)]
                MedicalRecord.objects.create(patient=patient, doctor=doctor, diagnosis=diagnosis, treatment=treatment)
                st.success("Medical record added!")

def patient_dashboard():
    st.title("Patient Dashboard")
    patient = Patient.objects.get(id=st.session_state.user_id)
    st.write(f"Welcome, {patient.user.first_name} {patient.user.last_name}")
    
    menu = st.sidebar.selectbox("Menu", ["My Appointments", "Book Appointment", "Medical Records"])
    
    if menu == "My Appointments":
        st.subheader("My Appointments")
        appointments = Appointment.objects.filter(patient=patient)
        for a in appointments:
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{a.doctor}** on {a.date} at {a.time} - Status: {a.status}")
            if col2.button("Cancel", key=f"cancel_{a.id}"):
                a.status = "CANCELLED"
                a.save()
                st.rerun()
    
    elif menu == "Book Appointment":
        st.subheader("Book Appointment")
        doctors = Doctor.objects.all()
        doctor_names = [f"Dr. {d.user.first_name} {d.user.last_name} ({d.specialty.name})" for d in doctors]
        
        with st.form("book_appointment"):
            doctor_name = st.selectbox("Select Doctor", doctor_names)
            appt_date = st.date_input("Date")
            appt_time = st.time_input("Time")
            
            if st.form_submit_button("Book Appointment"):
                doctor = doctors[doctor_names.index(doctor_name)]
                Appointment.objects.create(patient=patient, doctor=doctor, date=appt_date, time=appt_time)
                st.success("Appointment booked!")
                st.rerun()
    
    elif menu == "Medical Records":
        st.subheader("My Medical Records")
        records = MedicalRecord.objects.filter(patient=patient)
        for r in records:
            st.write(f"**Date:** {r.date}")
            st.write(f"**Doctor:** {r.doctor}")
            st.write(f"**Diagnosis:** {r.diagnosis}")
            st.write(f"**Treatment:** {r.treatment}")
            st.write("---")

# Main app
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_type = None
        st.session_state.user_id = None
        st.rerun()
    
    if st.session_state.user_type == "admin":
        admin_dashboard()
    elif st.session_state.user_type == "doctor":
        doctor_dashboard()
    elif st.session_state.user_type == "patient":
        patient_dashboard()
else:
    login_page()