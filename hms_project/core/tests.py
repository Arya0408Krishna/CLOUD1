from django.test import TestCase, Client
from django.contrib.auth.models import User
from core.models import Specialty
from patient_app.models import Patient
from doctor_app.models import Doctor, Appointment, MedicalRecord
from datetime import date, time

class ModelTests(TestCase):
    
    def setUp(self):
        # Create test users
        self.patient_user = User.objects.create_user(
            username='patient1',
            email='patient@test.com',
            password='test123',
            first_name='John',
            last_name='Doe'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor1',
            email='doctor@test.com',
            password='test123',
            first_name='Jane',
            last_name='Smith'
        )
        
        # Create specialty
        self.specialty = Specialty.objects.create(name='Cardiology')
        
        # Create patient
        self.patient = Patient.objects.create(
            user=self.patient_user,
            age=30,
            gender='M',
            contact='1234567890',
            address='123 Main St',
            date_of_birth=date(1993, 1, 1)
        )
        
        # Create doctor
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty=self.specialty,
            contact='9876543210'
        )
    
    def test_specialty_creation(self):
        """Test specialty model"""
        self.assertEqual(str(self.specialty), 'Cardiology')
        self.assertEqual(Specialty.objects.count(), 1)
    
    def test_patient_creation(self):
        """Test patient model"""
        self.assertEqual(str(self.patient), 'John Doe')
        self.assertEqual(self.patient.age, 30)
        self.assertEqual(Patient.objects.count(), 1)
    
    def test_doctor_creation(self):
        """Test doctor model"""
        self.assertEqual(str(self.doctor), 'Dr. Jane Smith')
        self.assertEqual(self.doctor.specialty.name, 'Cardiology')
        self.assertEqual(Doctor.objects.count(), 1)
    
    def test_appointment_creation(self):
        """Test appointment model"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=date(2024, 1, 15),
            time=time(10, 0),
            status='BOOKED'
        )
        self.assertEqual(appointment.status, 'BOOKED')
        self.assertEqual(Appointment.objects.count(), 1)
    
    def test_medical_record_creation(self):
        """Test medical record model"""
        record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis='Common Cold',
            treatment='Rest and fluids'
        )
        self.assertIsNotNone(record.date)
        self.assertEqual(MedicalRecord.objects.count(), 1)
    
    def test_appointment_status_choices(self):
        """Test appointment status transitions"""
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=date(2024, 1, 15),
            time=time(10, 0)
        )
        self.assertEqual(appointment.status, 'BOOKED')
        
        appointment.status = 'CANCELLED'
        appointment.save()
        self.assertEqual(appointment.status, 'CANCELLED')

class ViewTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
    
    def test_home_page(self):
        """Test home page loads"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hospital Management System')
    
    def test_admin_login(self):
        """Test admin login"""
        response = self.client.post('/admin/login/', {
            'username': 'admin',
            'password': 'admin123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_admin_access(self):
        """Test admin panel access"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

class IntegrationTests(TestCase):
    
    def setUp(self):
        # Create complete test data
        self.specialty = Specialty.objects.create(name='Pediatrics')
        
        self.patient_user = User.objects.create_user(
            username='patient_test',
            password='test123',
            first_name='Test',
            last_name='Patient'
        )
        
        self.doctor_user = User.objects.create_user(
            username='doctor_test',
            password='test123',
            first_name='Test',
            last_name='Doctor'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            age=25,
            gender='F',
            contact='1111111111',
            address='Test Address',
            date_of_birth=date(1998, 5, 15)
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            specialty=self.specialty,
            contact='2222222222'
        )
    
    def test_complete_appointment_workflow(self):
        """Test complete appointment booking workflow"""
        # Create appointment
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=date(2024, 2, 1),
            time=time(14, 30),
            status='BOOKED'
        )
        
        # Verify appointment
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.doctor, self.doctor)
        
        # Add medical record
        record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis='Routine Checkup',
            treatment='All normal'
        )
        
        # Complete appointment
        appointment.status = 'COMPLETED'
        appointment.save()
        
        # Verify workflow
        self.assertEqual(appointment.status, 'COMPLETED')
        self.assertEqual(MedicalRecord.objects.filter(patient=self.patient).count(), 1)
    
    def test_patient_multiple_appointments(self):
        """Test patient can have multiple appointments"""
        for i in range(3):
            Appointment.objects.create(
                patient=self.patient,
                doctor=self.doctor,
                date=date(2024, 1, i+1),
                time=time(10, 0),
                status='BOOKED'
            )
        
        self.assertEqual(Appointment.objects.filter(patient=self.patient).count(), 3)
    
    def test_doctor_multiple_patients(self):
        """Test doctor can have multiple patients"""
        for i in range(3):
            user = User.objects.create_user(
                username=f'patient{i}',
                password='test123'
            )
            patient = Patient.objects.create(
                user=user,
                age=20+i,
                gender='M',
                contact=f'111111111{i}',
                address='Test',
                date_of_birth=date(2000, 1, 1)
            )
            Appointment.objects.create(
                patient=patient,
                doctor=self.doctor,
                date=date(2024, 1, 15),
                time=time(10+i, 0),
                status='BOOKED'
            )
        
        self.assertEqual(Appointment.objects.filter(doctor=self.doctor).count(), 3)