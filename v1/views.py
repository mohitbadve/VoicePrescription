from django.shortcuts import render
import pymysql
import speech_recognition as sr
import googletrans
from googletrans import Translator
from fpdf import FPDF
from django.conf import settings
from django.core.mail import EmailMessage
import qrcode
import pyrebase
from django.shortcuts import redirect

checkIfRecording = -1
main_text = ""

firebaseConfig = {
    'apiKey': "AIzaSyCrXBHU_5S4tmWLQOaQIVvoRjjUeOfQjm0",
    'authDomain': "voice-prescription-dddb8.firebaseapp.com",
    'databaseURL': "https://voice-prescription-dddb8.firebaseio.com",
    'projectId': "voice-prescription-dddb8",
    'storageBucket': "voice-prescription-dddb8.appspot.com",
    'messagingSenderId': "653388576343",
    'appId': "1:653388576343:web:9228bb9c02721624709512"
}
firebase = pyrebase.initialize_app(firebaseConfig)
database=firebase.database()

def logout(request):
    try:
        del request.session['user_id']
        del request.session['user_name']
        return render(request,'index.html')
    except:
        return render(request,'index.html')

def index(request):
    if request.method == "POST":
        lic_no = request.POST.get('lic_no')
        password = request.POST.get('password')
        print(lic_no, password)
        con = pymysql.connect('db4free.net', 'mohit2000', 'Mohit@2K', 'voicepres')

        with con:
            cur = con.cursor()
            sql = "SELECT * FROM `users` WHERE lic_no = %s and password = %s"
            cur.execute(sql,(lic_no,password))
            data = cur.fetchall()
            print(data)
            if(len(data) == 1):
                request.session['user_name'] = str(data[0][4])
                request.session['user_id'] = str(data[0][2])
                return render(request, 'record_audio.html',{'name':data[0][4],'stat':''})
        return render(request,'e403.html')
    else:
        try:
            if request.session['user_id']:
                return render(request, 'record_audio.html',{'name':request.session['user_name'],'stat':''})
        except:
            return render(request, 'index.html')



def signup(request):
    if request.method == "POST":
        lic_no = request.POST.get('lic_no')
        mob_no = request.POST.get('mob_no')
        password = request.POST.get('password')
        name = request.POST.get('name')

        con = pymysql.connect('db4free.net', 'mohit2000', 'Mohit@2K', 'voicepres')

        with con:
            cur = con.cursor()
            sql = "INSERT INTO `users` VALUES (%s,%s, %s,%s,%s)"
            cur.execute(sql, (0,password,lic_no,mob_no,name))
            con.commit()

        print("Done")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(lic_no))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(r'static/qrcodes/qr' + str(lic_no) + '.jpg')
        print(img)
        return render(request,'print_qr_code.html',{'user_id':lic_no,'signup':'1','name':name})
    else:
        return render(request, 'signup.html')


def view_patient_history(request):

    return render(request,'view_patient_history.html',{'name':request.session['user_name']})

def view_doctor_history(request):
    return render(request,'view_doctor_history.html',{'name':request.session['user_name']})

def record_audio_start(request):
    global checkIfRecording
    if checkIfRecording == -1:
        checkIfRecording = 1
    global main_text
    translatedHindi = ""
    translatedMarathi = ""
    # obtain audio from the microphone
    while(checkIfRecording == 1):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
        # recognize speech using Google Speech Recognition
        try:
            new_text = r.recognize_google(audio)
            main_text = main_text + "\n" + new_text
            print("Google Speech Recognition thinks you said " + new_text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        print(main_text)

    #NLP

    #EDIT
    return render(request,'edit_prescription.html',{'draft':main_text})

def record_audio_stop(request):
    global checkIfRecording
    checkIfRecording = 0
    return redirect(record_audio_start)

def record_audio_nav(request):
    return render(request,'record_audio.html',{'name':request.session['user_name'],'stat':''})


def print_qr_code(request):
    return render(request,'print_qr_code.html',{'user_id':request.session['user_id'],'signup':'0','name':request.session['user_name']})


def edit_prescription(request):
    updated_prescription = request.POST.get('prescription')
    translator = Translator()
    translatedHindi = translator.translate(updated_prescription, src='en', dest='hi')
    translatedMarathi = translator.translate(updated_prescription, src='en', dest='mr')
    print(translatedHindi.text)
    print(translatedMarathi.text)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.write(5,updated_prescription)
    pdf.output("pres_English.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('gargi', '', 'gargi.ttf', uni=True)
    pdf.set_font('gargi', '', 14)
    s = translatedHindi.text
    pdf.write(5,s)
    pdf.output("pres_Hindi.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('gargi', '', 'gargi.ttf', uni=True)
    pdf.set_font('gargi', '', 14)
    s = translatedMarathi.text
    pdf.write(5,s)
    pdf.output("pres_Marathi.pdf")
    cur_patient = database.child("cur_patient").child(request.session['user_id']).get().val()
    print(cur_patient)
    cur_patient_email_id = database.child(cur_patient).child('email_id').get().val()
    return render(request,'mail_prescription.html',{'patient':cur_patient_email_id})

def mail_prescription(request):
    cur_patient_email_id = request.POST.get('patient')
    english = request.POST.get('English')
    hindi = request.POST.get('Hindi')
    marathi = request.POST.get('Marathi')
    print(english,hindi,marathi)
    email = EmailMessage(
        'Prescription from ' + str(request.session['user_name']),
        'Thank you for using DocAid.\nPlease find attached prescription',
        settings.EMAIL_HOST_USER,
        [cur_patient_email_id],
        ['mohit.badve@spit.ac.in'],  # bcc
    )
    if english:
        email.attach_file('pres_English.pdf')
    if hindi:
        email.attach_file('pres_Hindi.pdf')
    if marathi:
        email.attach_file('pres_Marathi.pdf')
    email.send()
    return render(request,'index.html')