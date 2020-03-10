from django.shortcuts import render
import pymysql
import speech_recognition as sr
import googletrans
from googletrans import Translator


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
                request.session['user_id'] = str(data[0][0])
                return render(request, 'doctor_index.html',{'name':data[0][4]})
        return render(request,'e403.html')
    else:
        try:
            if request.session['user_id']:
                return render(request, 'doctor_index.html',{'name':request.session['user_name']})
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
        return render(request, 'doctor_index.html')
    else:
        return render(request, 'signup.html')


def view_patient_history(request):
    print(googletrans.LANGUAGES)
    return render(request,'view_patient_history.html')

def view_doctor_history(request):
    return render(request,'view_doctor_history.html')

def record_audio_start(request):

    main_text = ""
    # obtain audio from the microphone
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)
    # recognize speech using Google Speech Recognition
    try:
        new_text = r.recognize_google(audio)
        main_text = main_text + new_text
        print("Google Speech Recognition thinks you said " + new_text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
    print(main_text)
    translator = Translator()
    translatedHindi = translator.translate(main_text, src='en', dest='hi')
    translatedMarathi = translator.translate(main_text, src='en', dest='mr')
    print(translatedHindi.text)
    print(translatedMarathi.text)
    return render(request,'doctor_index.html')

def record_audio_stop(request):

    main_text = ""
    # obtain audio from the microphone
    r = sr.Recognizer()
    while():
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
        # recognize speech using Google Speech Recognition
        try:
            new_text = r.recognize_google(audio)
            main_text = main_text + new_text
            print("Google Speech Recognition thinks you said " + new_text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
    print(main_text)
    return render(request,'doctor_index.html')

def record_audio_nav(request):
    return render(request,'record_audio.html')
