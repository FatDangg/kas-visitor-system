from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from flask_cors import CORS
import os
import json
import time
import threading
from pynput.mouse import Button, Controller

# Initialize Flask app and extensions
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///visitors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Visitor model
class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    visit_date = db.Column(db.String(20), nullable=False)
    pdf_path = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

PDF_DIR = "pdfs"
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# ----------------- PDF Generation Function ----------------- #
def generate_pdf(file_path, name, id_number, reason, visit_date):
    # Define custom page size: 62mm width and 100mm height
    page_width = 62 * 2 * mm   # 124 mm in points
    page_height = 48 * 2 * mm  # 96 mm in points
    pdf_canvas = canvas.Canvas(file_path, pagesize=(page_width, page_height))
    
    # Draw header with doubled font size and adjusted position
    pdf_canvas.setFont("Helvetica-Bold", 24)  # Double of 12
    pdf_canvas.drawCentredString(page_width / 2, page_height - 40, "Visitor Badge")  # y-offset doubled
    
    # Draw visitor details with doubled font size and adjusted positions
    pdf_canvas.setFont("Helvetica", 20)  # Double of 10
    pdf_canvas.drawString(20, page_height - 80, f"Name: {name}")     # x and y positions roughly doubled
    pdf_canvas.drawString(20, page_height - 110, f"ID: {id_number}")
    pdf_canvas.drawString(20, page_height - 140, f"Reason: {reason}")
    pdf_canvas.drawString(20, page_height - 170, f"Date: {visit_date}")
    
    # Add logo at bottom right scaled to 10% of its original size
    logo_path = "logo.png"  # Ensure this file is in the correct location
    try:
        logo = ImageReader(logo_path)
        original_logo_width, original_logo_height = logo.getSize()
        scale_factor = 0.08  # Adjust scale factor as desired (4% here)
        scaled_logo_width = original_logo_width * scale_factor
        scaled_logo_height = original_logo_height * scale_factor
        
        # Set a small margin from the bottom-right edge
        margin = 2 * mm
        x_logo = page_width - scaled_logo_width - margin
        y_logo = margin  # Place it at the bottom with a margin
        
        pdf_canvas.drawImage(
            logo, 
            x_logo, y_logo, 
            width=scaled_logo_width, 
            height=scaled_logo_height, 
            preserveAspectRatio=True, 
            mask='auto'
        )
    except Exception as e:
        print("Error loading logo:", e)
    
    pdf_canvas.save()

# ----------------- Mouse Replay Function ----------------- #
def replay_events(events_file="python_record_mouse/mouse_events.json", speed_factor=0.2, start_position=(100, 100)):
    """
    Reads a JSON file with recorded mouse events and replays them.
    """
    print("Mouse replay will start in 5 seconds. Prepare your system.")
    time.sleep(5)
    # 1. Load events
    try:
        with open(events_file, 'r') as f:
            events = json.load(f)
    except Exception as e:
        print(f"Error loading events file: {e}")
        return

    mouse_controller = Controller()

    # 2. Set starting position
    mouse_controller.position = start_position
    print(f"Starting position set to {start_position}")

    if not events:
        print("No events to replay. Exiting.")
        return

    start_time = events[0][-1]  # Timestamp of the first event
    print(f"Replaying events from {events_file} at speed factor = {speed_factor}.")
    for event in events:
        event_type = event[0]  # "move", "click", or "scroll"
        x = event[1]
        y = event[2]
        extra_1 = event[3]
        extra_2 = event[4]
        event_time = event[-1]

        # Calculate wait time
        wait_time = (event_time - start_time) * speed_factor
        time.sleep(wait_time)

        if event_type == "move":
            mouse_controller.position = (x, y)
        elif event_type == "click":
            button = Button.left if extra_1 == 'Button.left' else Button.right
            if extra_2:  # If pressed
                mouse_controller.press(button)
            else:  # If released
                mouse_controller.release(button)
        elif event_type == "scroll":
            dx = extra_1
            dy = extra_2
            mouse_controller.scroll(dx, dy)
        
        start_time = event_time

    print("Mouse events replayed.")

# ----------------- Flask Routes ----------------- #
@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json
    name = data.get('name')
    id_number = data.get('idNumber')
    reason = data.get('reason')
    visit_date = data.get('visitDate')

    if not all([name, id_number, reason, visit_date]):
        return jsonify({"error": "All fields are required!"}), 400

    file_name = f"visitor_{id_number}.pdf"
    file_path = os.path.join(PDF_DIR, file_name)
    generate_pdf(file_path, name, id_number, reason, visit_date)

    visitor = Visitor(
        name=name,
        id_number=id_number,
        reason=reason,
        visit_date=visit_date,
        pdf_path=file_path
    )
    db.session.add(visitor)
    db.session.commit()

    # After printing, execute the mouse replay function in a separate thread
    threading.Thread(target=replay_events, kwargs={
        "events_file": "python_record_mouse/mouse_events.json",
        "speed_factor": 0.2,
        "start_position": (100, 100)
    }).start()

    return jsonify({
        "message": "PDF generated successfully!",
        "downloadLink": f"/pdfs/{file_name}"
    })

@app.route('/pdfs/<filename>', methods=['GET'])
def download_pdf(filename):
    file_path = os.path.join(PDF_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
