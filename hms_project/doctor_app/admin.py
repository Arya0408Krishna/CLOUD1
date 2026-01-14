from django.contrib import admin
from .models import Doctor, Appointment, MedicalRecord

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialty', 'contact']
    search_fields = ['user__first_name', 'user__last_name', 'specialty__name']
    list_filter = ['specialty']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'time', 'status']
    search_fields = ['patient__user__first_name', 'doctor__user__first_name']
    list_filter = ['status', 'date', 'doctor__specialty']

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date']
    search_fields = ['patient__user__first_name', 'doctor__user__first_name']
    list_filter = ['date', 'doctor__specialty']