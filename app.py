from flask import Flask, render_template, request
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import random
import qrcode

app = Flask(__name__)

# Database to store ticket information
database = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_ticket', methods=['GET', 'POST'])
def generate_ticket():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact_details = request.form['contact_details']
        age = int(request.form['age'])
        phone_number = request.form['phone_number']

        # Generate a unique ticket ID
        ticket_id = random.randint(1000, 9999)

        # Store ticket information in the database
        database[ticket_id] = {
            "Name": name,
            "Email": email,
            "Contact Details": contact_details,
            "Age": age,
            "Phone Number": phone_number
        }

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(str(ticket_id))
        qr.make(fit=True)
        qr_image = qr.make_image(fill="black", back_color="white")
        qr_image.save(f"tgs2/qrcodes/{ticket_id}.png")

        return render_template('ticket_generated.html', ticket_id=ticket_id)

    return render_template('generate_ticket.html')

@app.route('/verify_ticket', methods=['GET', 'POST'])
def verify_ticket():
    if request.method == 'GET':
        return render_template('verify_ticket.html')
    elif request.method == 'POST':
        # Access the camera feed and scan the QR code
        cap = cv2.VideoCapture(0)
        found = False

        while not found:
            _, frame = cap.read()
            decoded_objects = pyzbar.decode(frame)

            for obj in decoded_objects:
                ticket_id = int(obj.data)
                if ticket_id in database:
                    # Ticket is verified, display ticket information
                    ticket_info = database[ticket_id]
                    found = True
                    break

            cv2.imshow("QR Code Scanner", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if found:
            return render_template('ticket_verified.html', ticket_info=ticket_info)
        else:
            return render_template('invalid_ticket.html')

    return render_template('verify_ticket.html')

if __name__ == '__main__':
    app.run(debug=True)