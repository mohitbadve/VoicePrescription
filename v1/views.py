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
import datetime
import pandas as pd
from bokeh.plotting import figure
from bokeh.embed import components

uName = ''
w = -1
main_text = ""
whatToSay = ['Patient Name','Symptoms','Diagnosis','Medicines','Dosage','Advice']
checkRecordings = [-1,-1,-1,-1,-1,-1]
prescription_data = [[] for i in range(6)]

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
class PDF(FPDF):
    def header(self):
        self.image(r'static/images/docaid_logo.png', 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'Prescription', 1, 0, 'C')
        self.ln(50)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Prescription From Dr.' + uName , 0, 0, 'C')

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
                return render(request, 'record_audio.html',{'whatToSay':'Press Start Recording','name':request.session['user_name'],'stat':''})
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
    cur_patient = database.child("cur_patient").child(request.session['user_id']).get().val()
    print(cur_patient)
    patient_id = "1"
    con = pymysql.connect('db4free.net', 'mohit2000', 'Mohit@2K', 'voicepres')
    with con:
        cur = con.cursor()
        q = "SELECT * FROM `patient_data` WHERE `patient_id`= "+patient_id
        df = pd.read_sql(q, con=con)
        x = list(df['date_of_visit'])
        y1 = list(df['bp'])
        y2 = list(df['sugar'])
        plot = figure(title='bp rate ',
                      x_axis_label='date_of_visit',
                      y_axis_label='bp',
                      plot_width=600,
                      plot_height=600)

        plot.line(x, y1, legend='f(x)', line_width=2)
        script, div = components(plot)

        plot2 = figure(title='sugar rate ',
                      x_axis_label='date_of_visit',
                      y_axis_label='sugar',
                      plot_width=600,
                      plot_height=600)

        plot2.line(x, y2, legend='f(x)', line_width=2)
        script2, div2 = components(plot2)

        print(df)
    return render(request,'view_patient_history.html',{'name':request.session['user_name'],'script': script, 'div': div,'script2': script2, 'div2': div2})

def view_doctor_history(request):
    doctor_id = request.session['user_id']
    #doctor_id = "007"
    con = pymysql.connect('db4free.net', 'mohit2000', 'Mohit@2K', 'voicepres')
    with con:
        cur = con.cursor()
        query = "SELECT * FROM `patient_data` WHERE `doctor_id` = %s "
        cur.execute(query,doctor_id)
        res = cur.fetchall()
        # print(res)
    return render(request,'view_doctor_history.html',{'name':request.session['user_name'],'res':res})

def record_audio_start(request):
    global w
    global checkRecordings
    if w != -1:
        if checkRecordings[w] == -1:
            checkRecordings[w] = 1
        global main_text
        global prescription_data
        # obtain audio from the microphone
        while(checkRecordings[w] == 1):
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Say something!")
                audio = r.listen(source)
            # recognize speech using Google Speech Recognition
            try:
                new_text = r.recognize_google(audio)
                if new_text:
                    if new_text != None and new_text not in prescription_data[w]:
                        prescription_data[w].append(new_text)
                print("Google Speech Recognition thinks you said " + new_text)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            print(prescription_data[w])



    print(w,'In Start')
    if w == -1:
        w += 1
        return render(request,'record_audio.html',{'whatToSay':whatToSay[0],'name':request.session['user_name']})
    if w == 6:
        for i in range(len(prescription_data)):
            prescription_data[i] = "".join(prescription_data[i])
        print(prescription_data)
        return render(request,'edit_prescription.html',{'draft':prescription_data,'name':request.session['user_name']})

def record_audio_stop(request):
    global checkRecordings
    global w
    if w != -1:
        checkRecordings[w] = 0
    print(w, 'In Stop')
    w += 1
    if w == 6:
        for i in range(len(prescription_data)):
            prescription_data[i] = "".join(prescription_data[i])
        print(prescription_data)
        return render(request,'edit_prescription.html',{'draft':prescription_data,'name':request.session['user_name']})
    return render(request,'record_audio.html',{'whatToSay':whatToSay[w],'name':request.session['user_name']})

def record_audio_nav(request):
    return render(request,'record_audio.html',{'whatToSay':'Press Start Recording','name':request.session['user_name'],'stat':''})


def print_qr_code(request):
    return render(request,'print_qr_code.html',{'user_id':request.session['user_id'],'signup':'0','name':request.session['user_name']})


def edit_prescription(request):
    def translateIntoMH(s):
        translator = Translator()
        return translator.translate(s, src='en', dest='hi').text,translator.translate(s, src='en', dest='mr').text

    global w,uName
    uName = request.session['user_name']
    w = 0
    name = request.POST.get('name')
    symptoms = request.POST.get('symptoms')
    medicines = request.POST.get('medicines')
    advice = request.POST.get('advice')
    diagnosis = request.POST.get('diagnosis')
    dosage = request.POST.get('dosage')
    
    nameTH,nameTM = translateIntoMH('name')
    symptomsTH, symptomsTM  = translateIntoMH('symptoms')
    diagnosisTH, diagnosisTM = translateIntoMH('diagnosis')
    medicinesTH, medicinesTM = translateIntoMH('medicines')
    dosageTH, dosageTM = translateIntoMH('dosage')
    adviceTH, adviceTM = translateIntoMH('advice')

    nameH,nameM = translateIntoMH(name)
    symptomsH,symptomsM = translateIntoMH(symptoms)
    medicinesH,medicinesM = translateIntoMH(medicines)
    adviceH,adviceM = translateIntoMH(advice)
    diagnosisH,diagnosisM = translateIntoMH(diagnosis)
    dosageH,dosageM = translateIntoMH(dosage)

    english_pres = [['Name',name],['Symptoms',symptoms],['Diagnosis',diagnosis],['Medicines',medicines],['Dosage',dosage],['Advice',advice]]
    hindi_pres = [[nameTH,nameH],[symptomsTH,symptomsH],[diagnosisTH,diagnosisH],[medicinesTH,medicinesH],[dosageTH,dosageH],[adviceTH,adviceH]]
    marathi_pres = [[nameTM,nameM],[symptomsTM,symptomsM],[diagnosisTM,diagnosisM],[medicinesTM,medicinesM],[dosageTM,dosageM],[adviceTM,adviceM]]
    today = datetime.date.today()
    today = today.strftime('%Y-%m-%d')
    cur_patient = str(database.child("cur_patient").child(request.session['user_id']).get().val())
    print(cur_patient)



    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Times', '', 14)
    pdf.ln(0.5)
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 2
    th = pdf.font_size
    for row in english_pres:
        for datum in row:
            pdf.cell(col_width, 2 * th, str(datum), border=1)
        pdf.ln(2 * th)
    pdf.output(r'static/pres/' + cur_patient + '_' + today + '_' + "pres_English.pdf",dest = 'F')

    pdf = PDF()
    pdf.add_page()
    pdf.add_font('gargi', '', 'gargi.ttf', uni=True)
    pdf.set_font('gargi', '', 14)
    pdf.ln(0.5)
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 2
    th = pdf.font_size
    for row in hindi_pres:
        for datum in row:
            pdf.cell(col_width, 2 * th, str(datum), border=1)
        pdf.ln(2 * th)
    pdf.output(r'static/pres/' + cur_patient + '_' + today + '_' + "pres_Hindi.pdf", dest='F')

    pdf = PDF()
    pdf.add_page()
    pdf.add_font('gargi', '', 'gargi.ttf', uni=True)
    pdf.set_font('gargi', '', 14)
    pdf.ln(0.5)
    epw = pdf.w - 2 * pdf.l_margin
    col_width = epw / 2
    th = pdf.font_size
    for row in marathi_pres:
        for datum in row:
            pdf.cell(col_width, 2 * th, str(datum), border=1)
        pdf.ln(2 * th)
    pdf.output(r'static/pres/' + cur_patient + '_' + today + '_' + "pres_Marathi.pdf", dest='F')

    # pdf = PDF()
    # pdf.add_page()
    # pdf.add_font('gargi', '', 'gargi.ttf', uni=True)
    # pdf.set_font('gargi', '', 14)
    # s =
    # pdf.write(5, s)
    # pdf.output(r'static/pres/' + cur_patient + '_' + today + '_' + "pres_Hindi.pdf",dest = 'F')
    #
    # pdf = PDF()
    # pdf.add_page()
    # pdf.add_font('gargi', '', 'gargi.ttf', uni=True)
    # pdf.set_font('gargi', '', 14)
    # s =
    # pdf.write(5, s)
    # pdf.output(r'static/pres/' + cur_patient + '_' + today + '_' + "pres_Marathi.pdf",dest = 'F')


    cur_patient_email_id = database.child(cur_patient).child('email_id').get().val()
    return render(request,'mail_prescription.html',{'pres_english':r'pres/' + cur_patient + '_' + today + '_' + "pres_English.pdf",
                                                    'pres_hindi': r'pres/' + cur_patient + '_' + today + '_' + "pres_Hindi.pdf",
                                                    'pres_marathi': r'pres/' + cur_patient + '_' + today + '_' + "pres_Marathi.pdf",
                                                    'patient':cur_patient_email_id,'name':request.session['user_name']})

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
    today = datetime.date.today()
    today = today.strftime('%Y-%m-%d')
    cur_patient = str(database.child("cur_patient").child(request.session['user_id']).get().val())
    if english:
        email.attach_file(r'static/pres/'+ cur_patient + '_' + today + '_' + "pres_English.pdf")
    if hindi:
        email.attach_file(r'static/pres/'+ cur_patient + '_' + today + '_' +"pres_Hindi.pdf")
    if marathi:
        email.attach_file(r'static/pres/'+ cur_patient + '_' + today +'_' + "pres_Marathi.pdf")
    email.send()
    return redirect(index)

def appointments(request):
    a = []
    today = datetime.date.today()
    today = today.strftime("%Y-%m-%d")
    print(today)
    print(request.session['user_id'])
    data = database.child('appointments').child(request.session['user_id']).child(today).get().val()
    print(data)
    for k,v in data.items():
        n = database.child(v).child('name').get().val()
        e = database.child(v).child('email_id').get().val()
        m = database.child(v).child('mob_no').get().val()
        a.append([k,[n,e,m]])

    return render(request,'appointments.html',{'appointments':a,'name':request.session['user_name']})