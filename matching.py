import face_recognition
import os
import shutil
import sqlite3
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from geopy.geocoders import Nominatim


def send_match_email(to_email, child_name, found_location, finders_contact_number, police_station_name):
    from_email = "missing_child@gmail.com" #must editable
    from_password = "app password" #must editable

    subject = "Good News! Your Child May Be Found"
    body = f"""
    Dear Parent,

    We may have found a match for your missing child: {child_name}.

   📍Found Location: {found_location}
   
    📞 Finder's Contact: {finders_contact_number}
    
    🚓 Nearest Police Station: {police_station_name}
    
    Please log in to the system: *link/matches* to verify the details and take appropriate action.

    Regards,
    Missing Child Detection System
    just ignore the mail, it's just a trial....
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")


def send_police_email(to_email, child_name, parent_contact_number, found_location, finders_contact_number):
    from_email = "missing_child@gmail.com" #must editable
    from_password = "app password" #must editable
    
    subject = "Child Match Alert: Immediate Attention Needed"
    body = f"""
    Dear Officer,

    A potential match for a missing child has been detected by our system in the area under your police station.

    Child's Name: {child_name}
    Parent's Contact: {parent_contact_number}
    Found Location: {found_location}
    Finder's Contact: {finders_contact_number}

    Please coordinate with the finder & child's family and verify the details in our system *link/matches*.

    Regards,
    Missing Child Detection System
    just ignore the mail, it's just a trial....
    """

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"📧 Alert sent to Police Station: {to_email}")
    except Exception as e:
        print(f"❌ Failed to send police email to {to_email}: {e}")

#--------------------------- Replacable by paid API -------------------------------
#----------------------------------------------------------------------------------
def get_coordinates(location):
    geolocator = Nominatim(user_agent="missing-child-locator")
    location_obj = geolocator.geocode(location + ", West Bengal, India")
    if location_obj:
        return location_obj.latitude, location_obj.longitude
    else:
        return None, None
#----------------------------------------------------------------------------------
def find_nearest_police_station(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    node
      [amenity=police]
      (around:10000,{lat},{lon});
    out;
    """

    try:
        response = requests.post(overpass_url, data=query, timeout=10)
        data = response.json()

        if data['elements']:
            stations = []
            for station in data['elements']:
                name = station.get('tags', {}).get('name', 'Unknown Police Station')
                email = station.get('tags', {}).get('email', 'Email not listed')
                stations.append((name, email))
            return stations
        else:
            return []
    except requests.exceptions.Timeout:
        return []
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []
#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------

# Define paths
missing_dir = "static/uploads_missing"
found_dir = "static/uploads_found"
matched_dir = "static/matched"
db_path = "database.db"

# Create matched folder if it doesn't exist
os.makedirs(matched_dir, exist_ok=True)

# Connect to SQLite DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create match_children table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS match_children (
        missing_id TEXT PRIMARY KEY,
        found_id TEXT,
        name TEXT,
        finders_contact TEXT,
        found_loc TEXT,
        parent_contact TEXT,
        mail TEXT,
        image_path TEXT
    )
''')
conn.commit()

# Loop through each image in uploads_missing
for missing_img_name in os.listdir(missing_dir):
    missing_img_path = os.path.join(missing_dir, missing_img_name)

    try:
        missing_image = face_recognition.load_image_file(missing_img_path)
        missing_encodings = face_recognition.face_encodings(missing_image)

        if not missing_encodings:
            print(f"No face found in {missing_img_name}")
            continue

        missing_encoding = missing_encodings[0]

        for found_img_name in os.listdir(found_dir):
            found_img_path = os.path.join(found_dir, found_img_name)
            found_image = face_recognition.load_image_file(found_img_path)
            found_encodings = face_recognition.face_encodings(found_image)

            if not found_encodings:
                print(f"No face found in {found_img_name}")
                continue

            for found_encoding in found_encodings:
                results = face_recognition.compare_faces([missing_encoding], found_encoding)

                if results[0]:
                    dest_path = os.path.join(matched_dir, missing_img_name)
                    shutil.copy(found_img_path, dest_path)

                    print(f"Match found: {missing_img_name} ↔ {found_img_name}")

                    missing_img_base = os.path.splitext(missing_img_name)[0]
                    found_img_base = os.path.splitext(found_img_name)[0]

                    cursor.execute("SELECT id, name, parent_contact, email FROM missing_children WHERE id = ?", (missing_img_base,))
                    missing_data = cursor.fetchone()

                    cursor.execute("SELECT id, finders_contact_number, found_location FROM found_children WHERE id = ?", (found_img_base,))
                    found_data = cursor.fetchone()

                    if missing_data and found_data:
                        missing_id, name, parent_contact, mail = missing_data
                        found_id, finders_contact, found_loc = found_data

                        cursor.execute("SELECT * FROM match_children WHERE missing_id = ?", (missing_id,))
                        existing_match = cursor.fetchone()

                        if not existing_match:
                            cursor.execute('''
                                INSERT INTO match_children (
                                    missing_id, found_id, name, finders_contact, found_loc, parent_contact, mail, image_path
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                missing_id, found_id, name, finders_contact, found_loc, parent_contact, mail, dest_path
                            ))
                            conn.commit()

                            # 🛰️ Locate nearest police station
                            lat, lon = get_coordinates(found_loc)
                            if lat and lon:
                             stations = find_nearest_police_station(lat, lon)
                             if stations:
                                 policestation_name, police_mail = stations[0]
                                 
                                 #("\n🚓 Nearest Police Station:")
                                 #print(f"Name: {policestation_name}")
                                 #print(f"Email: {police_mail}")
                         
                                 # Send both parent and police emails
                                 send_match_email(mail, name, found_loc, finders_contact, policestation_name)
                                 #send_police_email(police_mail, name, parent_contact, found_loc, finders_contact)
                             else:
                                 print("⚠️ No police stations found nearby.")
                                 send_match_email(mail, name, found_loc, finders_contact, "Not Available")
                            else:
                             print("❌ Could not geocode the location.")
                             send_match_email(mail, name, found_loc, finders_contact, "Not Available")
          
                        else:
                            print(f"⚠️ Match already exists for missing ID: {missing_id}")
                    else:
                        print("⚠️ Could not find matching DB records for one or both images.")

                    break
            else:
                continue
            break

    except Exception as e:
        print(f"Error processing {missing_img_name}: {e}")

conn.close()
