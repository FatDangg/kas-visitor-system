from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from flask import Flask
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database configuration
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

# Create the database tables
with app.app_context():
    db.create_all()

# Directory to store PDFs
PDF_DIR = "pdfs"
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# Generate PDF function
def generate_pdf(file_path, name, id_number, reason, visit_date):
    pdf_canvas = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    pdf_canvas.setFont("Helvetica-Bold", 20)
    pdf_canvas.drawCentredString(width / 2, height - 50, "Visitor Badge")

    pdf_canvas.setFont("Helvetica", 14)
    pdf_canvas.drawString(50, height - 100, f"Name: {name}")
    pdf_canvas.drawString(50, height - 130, f"ID: {id_number}")
    pdf_canvas.drawString(50, height - 160, f"Reason: {reason}")
    pdf_canvas.drawString(50, height - 190, f"Date: {visit_date}")

    pdf_canvas.save()

# Submit visitor data
@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json
    name = data.get('name')
    id_number = data.get('idNumber')
    reason = data.get('reason')
    visit_date = data.get('visitDate')

    if not all([name, id_number, reason, visit_date]):
        return jsonify({"error": "All fields are required!"}), 400

    # Generate PDF
    file_name = f"visitor_{id_number}.pdf"
    file_path = os.path.join(PDF_DIR, file_name)
    generate_pdf(file_path, name, id_number, reason, visit_date)

    # Save visitor to database
    visitor = Visitor(
        name=name,
        id_number=id_number,
        reason=reason,
        visit_date=visit_date,
        pdf_path=file_path
    )
    db.session.add(visitor)
    db.session.commit()

    return jsonify({
        "message": "PDF generated successfully!",
        "downloadLink": f"/download/{file_name}"
    })

# Download PDF
@app.route('/download/<filename>', methods=['GET'])
def download_pdf(filename):
    file_path = os.path.join(PDF_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({"error": "File not found!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
