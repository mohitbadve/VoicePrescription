"""voicePrescription URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from v1.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('login/', index),
    path('logout/', logout),
    path('signup/', signup),
    path('view_patient_history/', view_patient_history),
    path('view_doctor_history/', view_doctor_history),
    path('record_audio_nav/', record_audio_nav),
    path('record_audio_start/', record_audio_start),
    path('record_audio_stop/', record_audio_stop),
    path('print_qr_code/', print_qr_code),
    path('edit_prescription/', edit_prescription),
    path('mail_prescription/', mail_prescription),
    path('appointments/', appointments),
]
