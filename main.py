import requests
import time
import ssl
import json
from smtplib import SMTP
from shapely import Polygon, Point
from email.mime.text import MIMEText

NUM_OF_CLINICIANS = 6
POLLING_INTERVAL_IN_SECONDS = 30
URL = "https://3qbqr98twd.execute-api.us-west-2.amazonaws.com/test/clinicianstatus/"

PORT = 587
HOST = "smtp-mail.outlook.com"
EMAILER = SMTP(HOST, PORT)
EMAIL_RECEIVER = "epicwhale53@gmail.com"
LOGIN_EMAIL = "persont924@outlook.com"
LOGIN_PASSWORD = "bojack_horseman924"

def check_clinician_safety(coords):
    clinician_location = Point(coords["features"][0]["geometry"]["coordinates"])
    safe_zone = Polygon(coords["features"][1]["geometry"]["coordinates"][0])

    return safe_zone.contains(clinician_location)

def send_email(subject, message):
    email_content = MIMEText(message, "plain")
    email_content["From"] = LOGIN_EMAIL
    email_content["To"] = EMAIL_RECEIVER
    email_content["Subject"] = subject
    EMAILER.sendmail(LOGIN_EMAIL, EMAIL_RECEIVER, email_content.as_string())

def clinician_tracker():
    EMAILER.starttls(context=ssl.create_default_context())
    EMAILER.login(LOGIN_EMAIL, LOGIN_PASSWORD)
    clinician_locations = {}

    while True:
        for id in range(1, NUM_OF_CLINICIANS + 1):
            clinician_id = str(id)
            response = requests.get(URL + clinician_id)

            if response.ok:
                clinician_coords = response.json()
                clinician_moved = clinician_id not in clinician_locations or clinician_locations[clinician_id] is not clinician_coords
                
                if clinician_moved:
                    clinician_locations[clinician_id] = clinician_coords
                    is_clinician_safe = check_clinician_safety(clinician_coords)

                    if not is_clinician_safe:
                        subject = "Clinician " + clinician_id + " is not safe"
                        message = "Clinician " + clinician_id + " is not safe"
                        send_email(subject, message)
            else:
                subject = "Clinician status API is not working"
                message = json.dumps(response.json())
                send_email(subject, message)
        
        time.sleep(POLLING_INTERVAL_IN_SECONDS)


# start tracking
clinician_tracker()