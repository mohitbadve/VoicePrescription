# VoicePrescription

To run the project, first clone the repository or download and extract the zip file and install the required packages and dependencies using the command
> pip install -r requirements.txt

To run the Django project, execute the following command
> python manage.py runserver

Doctors have to enter their name, license number, mobile number, password in order to sign up.

![Alt text](screenshots/register.png?raw=true "Register")



After signing up, on the basis of their license number unique QR code will be generated. Printout of that can be taken at any point of time after logging in to stick it outside the clinic so that every patient can simply come in the clinic and scan the QR code through an android app.

![Alt text](screenshots/qr.png?raw=true "QR")



The graphs of the patient’s sugar rate and blood pressure rate will be plotted against the date of visit to see the progress of a patient which will help the doctor in analyzing how the health of the patient has improved  over time.
![Alt text](screenshots/history.png?raw=true "history")



Doctors will be able to edit the description at the end and then just press a button to mail the prescription in different languages to the current patient.

![Alt text](screenshots/file.png?raw=true "PDF")


