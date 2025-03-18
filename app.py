from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PIL import Image
import json
import tempfile
import uuid
from dotenv import load_dotenv
import sqlite3
import io
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.platypus import HRFlowable

# Load environment variables
load_dotenv()

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
CORS(app)

# Get email credentials from environment variables
EMAIL_USER = os.environ.get('EMAIL_USER')
EMAIL_PASS = os.environ.get('EMAIL_PASS')

# Default recipient for all forms
DEFAULT_RECIPIENT = 'tony1550@hotmail.com'

# Configuration
app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///invoices.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=EMAIL_USER,
    MAIL_PASSWORD=EMAIL_PASS,
    UPLOAD_FOLDER='uploads'
)

print(f"Email configuration: {app.config['MAIL_USERNAME']}")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Delete the database file if it exists to ensure a clean start
db_path = 'invoices.db'
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Removed existing database file: {db_path}")
    except Exception as e:
        print(f"Could not remove database file: {e}")

db = SQLAlchemy(app)
mail = Mail(app)

# Define the Invoice model
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)
    client_address = db.Column(db.Text, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    items = db.Column(db.Text)  # JSON string of items

# Define the Timecard model
class Timecard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    shift = db.Column(db.String(50), nullable=False)
    recipient_email = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.String(200), nullable=True)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    form_data = db.Column(db.Text)  # JSON string of all form data

# Define the Mileage model
class Mileage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    week_ending = db.Column(db.String(50), nullable=False)
    total_miles = db.Column(db.Float, nullable=False, default=0)
    reimbursement_amount = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    form_data = db.Column(db.Text, nullable=True)

# Serve Landing Page
@app.route('/')
def landing_page():
    return render_template('landing.html')

# Invoice System route
@app.route('/invoice')
def invoice_system():
    return render_template('index.html')

# Timecard form route
@app.route('/timecard')
def timecard_form():
    return render_template('timecard.html')

# Mileage report form route
@app.route('/mileage')
def mileage_form():
    return render_template('mileage.html')

# Test route to verify Flask is serving templates correctly
@app.route('/test')
def test_page():
    return render_template('test.html')

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# API routes should be defined before the catch-all route
@app.route('/api/invoice', methods=['POST'])
def create_invoice():
    try:
        # Get form data
        client_name = request.form['client_name']
        client_email = request.form['client_email']
        client_address = request.form['client_address']
        items = request.form['items']
        amount = float(request.form['amount'])
        
        print(f"Received invoice data: {client_name}, {client_email}, {amount}")
        
        # Create invoice record
        new_invoice = Invoice(
            invoice_number=f"INV-{datetime.now().strftime('%Y%m%d')}-{db.session.query(Invoice).count() + 1:03d}",
            client_name=client_name,
            client_email=client_email,
            client_address=client_address,
            amount=amount,
            items=items
        )
        
        db.session.add(new_invoice)
        db.session.commit()
        print(f"Invoice created with ID: {new_invoice.id}")
        
        # Generate PDF
        pdf_file = generate_pdf(new_invoice.__dict__)
        print(f"PDF generated at: {pdf_file}")
        
        # Check if email credentials are available
        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
            print("Email credentials not found. Skipping email sending.")
            # Clean up files
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
                
            return jsonify({
                "message": "Invoice created successfully (email not sent - credentials missing)",
                "id": new_invoice.id
            }), 200
        
        # Send email
        try:
            msg = Message(
                'Your Invoice from GruntCode',
                sender=app.config['MAIL_USERNAME'],
                recipients=[client_email],
                cc=[DEFAULT_RECIPIENT]  # CC the default recipient
            )
            msg.body = f"""
            Dear {client_name},
            
            Please find attached your invoice #{new_invoice.invoice_number}.
            
            Total Amount: ${amount:.2f}
            
            Billing Address:
            {client_address}
            
            Thank you for your business!
            
            Best regards,
            GruntCode Gaming Team
            Modern Solutions for Modern Gamers
            """
            with open(pdf_file, 'rb') as fp:
                msg.attach(
                    f"invoice_{new_invoice.invoice_number}.pdf",
                    "application/pdf",
                    fp.read()
                )
            mail.send(msg)
            print("Email sent successfully")
            
            # Clean up files
            os.remove(pdf_file)
                
            return jsonify({
                "message": "Invoice created and sent successfully",
                "id": new_invoice.id
            }), 200
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            # Still return success since the invoice was created
            return jsonify({
                "message": f"Invoice created but email failed: {str(e)}",
                "id": new_invoice.id
            }), 200
            
    except Exception as e:
        print(f"Error creating invoice: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/timecard', methods=['POST'])
def submit_timecard():
    try:
        # Get form data
        employee_name = request.form.get('employee-name')
        department = request.form.get('department')
        shift = request.form.get('shift')
        recipient_email = "timecardcorrection@MERITALUMINUM.COM"  # Hardcoded email address
        
        # Get reasons (checkboxes)
        reasons = request.form.getlist('reason')
        reason_text = ", ".join(reasons) if reasons else "Not specified"
        
        # Store all form data as JSON for database
        form_data = {}
        for key in request.form:
            if key != 'reason':  # Handle multiple values for reason separately
                form_data[key] = request.form.get(key)
        
        form_data['reasons'] = reasons
        
        # Create timecard record
        new_timecard = Timecard(
            employee_name=employee_name,
            department=department,
            shift=shift,
            recipient_email=recipient_email,
            reason=reason_text,
            form_data=json.dumps(form_data)
        )
        
        db.session.add(new_timecard)
        db.session.commit()
        print(f"Timecard created with ID: {new_timecard.id}")
        
        # Generate PDF
        pdf_file = generate_timecard_pdf(form_data)
        print(f"Timecard PDF generated at: {pdf_file}")
        
        # Check if email credentials are available
        if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
            print("Email credentials not found. Skipping email sending.")
            # Clean up files
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
                
            return jsonify({
                "message": "Timecard submitted successfully (email not sent - credentials missing)",
                "id": new_timecard.id
            }), 200
        
        # Send email
        try:
            msg = Message(
                'Timecard Correction Form Submission',
                sender=app.config['MAIL_USERNAME'],
                recipients=[recipient_email],
                cc=[DEFAULT_RECIPIENT]  # CC the default recipient
            )
            msg.body = f"""
            Timecard Correction Form Submission
            
            Employee: {employee_name}
            Department: {department}
            Shift: {shift}
            Reason: {reason_text}
            
            Please see the attached PDF for the complete timecard correction form.
            """
            with open(pdf_file, 'rb') as fp:
                msg.attach(
                    f"timecard_{new_timecard.id}.pdf",
                    "application/pdf",
                    fp.read()
                )
            mail.send(msg)
            print(f"Email sent successfully to {recipient_email} and CC to {DEFAULT_RECIPIENT}")
            
            # Clean up files
            os.remove(pdf_file)
                
            return jsonify({
                "message": "Timecard submitted and sent successfully",
                "id": new_timecard.id
            }), 200
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            # Still return success since the timecard was created
            return jsonify({
                "message": f"Timecard submitted but email failed: {str(e)}",
                "id": new_timecard.id
            }), 200
            
    except Exception as e:
        print(f"Error submitting timecard: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/mileage', methods=['POST'])
def submit_mileage():
    try:
        # Get form data
        form_data = request.form.to_dict()
        
        # Debug: Print received form data
        print("Received form data:", form_data)
        
        # Generate PDF
        try:
            pdf_path = generate_mileage_pdf(form_data)
            print("PDF generated successfully at:", pdf_path)
        except Exception as pdf_error:
            print(f"Error generating PDF: {str(pdf_error)}")
            return jsonify({"success": False, "error": f"PDF generation error: {str(pdf_error)}"}), 500
        
        # Parse numeric values
        try:
            total_miles = float(form_data.get('total-business-miles', 0))
        except ValueError as ve:
            print(f"Error parsing total miles: {str(ve)}")
            total_miles = 0
            
        try:
            reimbursement_amount = float(form_data.get('total-amount', 0))
        except ValueError as ve:
            print(f"Error parsing reimbursement amount: {str(ve)}")
            reimbursement_amount = 0
        
        # Save to database
        try:
            mileage = Mileage(
                employee_name=form_data.get('employee-name', ''),
                branch=form_data.get('branch', ''),
                week_ending=form_data.get('week-ending', ''),
                total_miles=total_miles,
                reimbursement_amount=reimbursement_amount,
                created_at=datetime.now(),
                form_data=json.dumps(form_data)
            )
            db.session.add(mileage)
            db.session.commit()
            print("Mileage data saved to database successfully")
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            return jsonify({"success": False, "error": f"Database error: {str(db_error)}"}), 500
        
        # Send email with PDF attachment
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            try:
                recipient_email = form_data.get('email', DEFAULT_RECIPIENT)
                employee_name = form_data.get('employee-name', 'Employee')
                
                msg = Message(
                    'Mileage Reimbursement Log Submission',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[recipient_email],
                    cc=[DEFAULT_RECIPIENT]  # CC the default recipient
                )
                msg.body = f"""
                Mileage Reimbursement Log Submission
                
                Employee: {employee_name}
                Branch: {form_data.get('branch', '')}
                Week Ending: {form_data.get('week-ending', '')}
                Total Miles: {total_miles}
                Reimbursement Amount: ${reimbursement_amount:.2f}
                
                Please see the attached PDF for the complete mileage reimbursement log.
                """
                with open(pdf_path, 'rb') as fp:
                    msg.attach(
                        f"mileage_{mileage.id}.pdf",
                        "application/pdf",
                        fp.read()
                    )
                mail.send(msg)
                print(f"Email sent successfully to {recipient_email} and CC to {DEFAULT_RECIPIENT}")
                
                # Clean up files
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
            except Exception as email_error:
                print(f"Error sending email: {str(email_error)}")
                # Continue even if email fails
        else:
            print("Email credentials not found. Skipping email sending.")
            # Clean up files
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        
        # Return success response
        print("Form submitted successfully")
        return jsonify({"success": True, "message": "Mileage report submitted successfully!"})
        
    except Exception as e:
        print(f"Error submitting mileage report: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    invoices = Invoice.query.all()
    result = []
    for invoice in invoices:
        invoice_dict = {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'client_name': invoice.client_name,
            'client_email': invoice.client_email,
            'amount': invoice.amount,
            'date_created': invoice.date_created.strftime('%Y-%m-%d'),
            'status': invoice.status,
            'items': json.loads(invoice.items) if invoice.items else []
        }
        result.append(invoice_dict)
    return jsonify(result)

@app.route('/api/invoice/<int:id>/status', methods=['PUT'])
def update_status(id):
    data = request.json
    invoice = Invoice.query.get_or_404(id)
    invoice.status = data['status']
    db.session.commit()
    return jsonify({"message": "Status updated successfully"})

@app.route('/api/invoice/<int:id>/paid', methods=['PUT'])
def mark_invoice_paid(id):
    invoice = Invoice.query.get_or_404(id)
    invoice.status = 'paid'
    invoice.amount = 0  # Zero out the invoice amount
    db.session.commit()
    return jsonify({"message": "Invoice marked as paid and zeroed out"})

# Handle React Router paths - this should be the last route
@app.route('/<path:path>')
def catch_all(path):
    # Only handle non-API routes with the catch-all
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('index.html')

def generate_pdf(invoice_data, logo_path=None):
    filename = os.path.join(tempfile.gettempdir(), f"invoice_{invoice_data['invoice_number']}.pdf")
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add GruntCode logo (permanent)
    # Create a cyberpunk-style logo directly in the PDF
    c.setFillColorRGB(0, 1, 1)  # Cyan
    c.rect(40, height - 120, 120, 80, fill=True)
    c.setFillColorRGB(1, 0, 1)  # Pink
    c.rect(50, height - 110, 100, 60, fill=True)
    c.setFillColorRGB(0.61, 0.15, 0.69)  # Purple
    c.setFont("Helvetica-Bold", 30)
    c.setFillColorRGB(0, 1, 0.62)  # Neon green
    c.drawString(60, height - 80, "GC")
    
    # Add invoice details with cyberpunk-inspired styling
    c.setFillColorRGB(0, 1, 1)  # Cyan color for header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(200, height - 100, "INVOICE")
    
    # Use black text for all invoice details for better visibility
    c.setFillColorRGB(0, 0, 0)  # Black color for text
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 150, f"Invoice #: {invoice_data['invoice_number']}")
    c.drawString(40, height - 170, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Add typical invoice information
    c.drawString(40, height - 190, f"Client: {invoice_data['client_name']}")
    c.drawString(40, height - 210, f"Email: {invoice_data['client_email']}")
    
    # Add payment terms and due date
    current_date = datetime.now()
    due_date = current_date + timedelta(days=30)  # 30-day payment terms
    c.drawString(350, height - 150, "Payment Terms: Net 30")
    c.drawString(350, height - 170, f"Due Date: {due_date.strftime('%Y-%m-%d')}")
    
    # Add invoice status
    status = invoice_data.get('status', 'pending').upper()
    c.drawString(350, height - 190, f"Status: {status}")
    
    # Add company information
    c.setFont("Helvetica", 10)
    c.drawString(350, height - 220, "GruntCode Gaming")
    c.drawString(350, height - 235, "123 Cyber Street")
    c.drawString(350, height - 250, "Silicon Valley, CA 94000")
    c.drawString(350, height - 265, "Phone: (555) 123-4567")
    c.drawString(350, height - 280, "Email: contact@gruntcode.com")
    
    # Add client address (new)
    if 'client_address' in invoice_data and invoice_data['client_address']:
        # Split address into lines
        address_lines = invoice_data['client_address'].split('\n')
        y_position = height - 230
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y_position, "Bill To:")
        y_position -= 20
        c.setFont("Helvetica", 10)
        for line in address_lines:
            c.drawString(40, y_position, line.strip())
            y_position -= 15
    else:
        y_position = height - 230
    
    # Add items table header with black text
    y_position = min(y_position, height - 300)  # Ensure we have enough space
    items = json.loads(invoice_data['items'])
    
    # Draw table header with light gray background
    c.setFillColorRGB(0.9, 0.9, 0.9)  # Light gray background
    c.rect(35, y_position - 5, width - 70, 25, fill=True)
    
    # Draw table header text in black
    c.setFillColorRGB(0, 0, 0)  # Black text
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y_position, "Description")
    c.drawString(300, y_position, "Quantity")
    c.drawString(370, y_position, "Unit Price")
    c.drawString(450, y_position, "Amount")
    y_position -= 25
    
    # Draw a horizontal line below the header
    c.setStrokeColorRGB(0, 0, 0)
    c.line(35, y_position + 5, width - 35, y_position + 5)
    
    # Add items with alternating background for better visibility
    for idx, item in enumerate(items):
        # Set background color for alternating rows
        if idx % 2 == 0:
            c.setFillColorRGB(0.95, 0.95, 0.95)  # Very light gray
        else:
            c.setFillColorRGB(1, 1, 1)  # White
        
        # Draw row background
        c.rect(35, y_position - 5, width - 70, 20, fill=True)
        
        # Draw item details in black text
        c.setFillColorRGB(0, 0, 0)  # Black text for better visibility
        c.setFont("Helvetica", 10)
        
        # Handle long descriptions by truncating or wrapping
        description = item['description']
        if len(description) > 35:
            description = description[:32] + "..."
            
        # Add quantity and unit price (default to 1 and amount if not provided)
        quantity = item.get('quantity', 1)
        unit_price = item.get('unit_price', item['amount'])
        
        c.drawString(40, y_position, description)
        c.drawString(300, y_position, str(quantity))
        c.drawString(370, y_position, f"${unit_price:.2f}")
        c.drawString(450, y_position, f"${item['amount']:.2f}")
        
        y_position -= 20
        
        # Add a light gray line between items
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.line(35, y_position - 5, width - 35, y_position - 5)
    
    # Draw a horizontal line below the items
    c.setStrokeColorRGB(0, 0, 0)
    c.line(35, y_position - 10, width - 35, y_position - 10)
    
    # Add subtotal, tax, and total with black text
    y_position -= 30
    c.setFillColorRGB(0, 0, 0)  # Black text
    c.setFont("Helvetica", 10)
    
    subtotal = invoice_data['amount']
    tax_rate = 0.0  # Default to 0% tax
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    c.drawRightString(400, y_position, "Subtotal:")
    c.drawString(450, y_position, f"${subtotal:.2f}")
    y_position -= 20
    
    c.drawRightString(400, y_position, f"Tax ({tax_rate*100:.0f}%):")
    c.drawString(450, y_position, f"${tax_amount:.2f}")
    y_position -= 20
    
    # Add total with slightly larger font
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(400, y_position, "Total:")
    c.drawString(450, y_position, f"${total:.2f}")
    
    # Add payment instructions
    y_position -= 40
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y_position, "Payment Instructions:")
    y_position -= 15
    c.setFont("Helvetica", 10)
    c.drawString(40, y_position, "Please make payment to GruntCode Gaming within 30 days of invoice date.")
    y_position -= 15
    c.drawString(40, y_position, "Bank Transfer: Bank of America - Account #: 1234567890 - Routing #: 026009593")
    
    # Add thank you note
    y_position -= 30
    c.drawString(40, y_position, "Thank you for your business!")
    
    # Add footer
    c.setFont("Helvetica", 8)
    c.drawString(width/2 - 100, 25, f"Invoice #{invoice_data['invoice_number']} - Generated on {datetime.now().strftime('%Y-%m-%d')}")
    
    c.save()
    return filename

def generate_timecard_pdf(form_data):
    # Create a temporary file for the PDF
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    # Create the PDF
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    width, height = letter
    
    # Set up styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading2'],
        alignment=1,  # Center alignment
        fontSize=12,
        leading=14,  # Increased line spacing
        spaceAfter=10
    )
    
    # Add header
    c.setFont("Helvetica-Bold", 20)
    c.drawString(width/2 - 50, height - 50, "MERIT")
    c.setFont("Helvetica", 14)
    c.drawString(width/2 - 60, height - 70, "ALUMINUM")
    
    # Add horizontal line
    c.line(50, height - 80, width - 50, height - 80)
    
    # Add title
    title = "Timecard Correction Form / Formato para Corrección de Tarjeta de Asistencia"
    p = Paragraph(title, title_style)
    p.wrapOn(c, width - 100, 40)  # Increased height for wrapping
    p.drawOn(c, 50, height - 115)
    
    # Add another horizontal line
    c.line(50, height - 125, width - 50, height - 125)
    
    # Employee information
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 150, "Employee Name/Nombre del empleado:")
    c.setFont("Helvetica", 10)
    c.drawString(250, height - 150, form_data.get('employee-name', ''))
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 180, "Department/Departamento:")
    c.setFont("Helvetica", 10)
    c.drawString(200, height - 180, form_data.get('department', ''))
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, height - 180, "Shift:")
    c.setFont("Helvetica", 10)
    c.drawString(400, height - 180, form_data.get('shift', ''))
    
    # Create timecard table
    days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    day_labels = ['Sunday/Domingo', 'Monday/Lunes', 'Tuesday/Martes', 'Wednesday/Miércoles', 
                  'Thursday/Jueves', 'Friday/Viernes', 'Saturday/Sábado']
    
    data = [['Date/Fecha', 'Time In\nTiempo de Entrada', 'Lunch Out', 'Lunch In', 
             'Time Out\nTiempo de Salida', 'Daily Total\nTotal Diario']]
    
    for i, day in enumerate(days):
        row = [
            day_labels[i],
            form_data.get(f'{day}-time-in', ''),
            form_data.get(f'{day}-lunch-out', ''),
            form_data.get(f'{day}-lunch-in', ''),
            form_data.get(f'{day}-time-out', ''),
            form_data.get(f'{day}-total', '')
        ]
        data.append(row)
    
    table = Table(data, colWidths=[100, 80, 80, 80, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    table.wrapOn(c, width - 100, 300)
    table.drawOn(c, 50, height - 350)
    
    # Reason section
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 380, "Reason:")
    
    reasons = form_data.get('reasons', [])
    if isinstance(reasons, str):
        reasons = [reasons]
    
    reason_options = [
        "Failed to record worked hours",
        "Forgot to Clock In/Out",
        "Incorrect Punch",
        "Time clock # Not Issued Yet",
        "Power Outage",
        "Time Clock Malfunction"
    ]
    
    y_pos = height - 400
    for i, option in enumerate(reason_options):
        x_pos = 50 if i < 3 else 300
        y_offset = (i % 3) * 20
        
        # Draw checkbox
        c.rect(x_pos, y_pos - y_offset, 10, 10, stroke=1, fill=0)
        if option in reasons:
            c.rect(x_pos, y_pos - y_offset, 10, 10, stroke=1, fill=1)
        
        # Draw label
        c.setFont("Helvetica", 10)
        c.drawString(x_pos + 15, y_pos - y_offset, option)
    
    # Verification text
    y_pos = height - 480
    c.setFont("Helvetica", 9)
    c.drawString(50, y_pos, "By signing below I acknowledge and verify that the changes to the daily hours for the work week")
    c.drawString(50, y_pos - 15, "listed above are accurate.")
    c.drawString(50, y_pos - 40, "Al firmar a continuación reconozco y rectifico que los cambios en la jornada de la semana de")
    c.drawString(50, y_pos - 55, "trabajo mencionados son exactos.")
    
    # Signature section
    y_pos = height - 550
    
    # Employee signature
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y_pos, "Employee's Name (Please print)")
    c.drawString(50, y_pos - 15, "Nombre del empleado (por favor impreso)")
    c.line(50, y_pos - 30, 200, y_pos - 30)
    c.setFont("Helvetica", 9)
    c.drawString(50, y_pos - 45, form_data.get('employee-print-name', ''))
    
    # Employee signature
    c.setFont("Helvetica-Bold", 9)
    c.drawString(220, y_pos, "Employee's Signature")
    c.drawString(220, y_pos - 15, "Firma del Empleado")
    c.line(220, y_pos - 30, 370, y_pos - 30)
    c.setFont("Helvetica", 9)
    c.drawString(220, y_pos - 45, form_data.get('employee-signature', ''))
    
    # Date
    c.setFont("Helvetica-Bold", 9)
    c.drawString(390, y_pos, "Date")
    c.drawString(390, y_pos - 15, "Fecha")
    c.line(390, y_pos - 30, 540, y_pos - 30)
    c.setFont("Helvetica", 9)
    c.drawString(390, y_pos - 45, form_data.get('date', ''))
    
    # Horizontal line
    c.line(50, y_pos - 60, width - 50, y_pos - 60)
    
    # Manager section
    y_pos = height - 620
    
    # Manager name
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y_pos, "Department Manager/Gerente de Departamento")
    c.line(50, y_pos - 15, 200, y_pos - 15)
    c.setFont("Helvetica", 9)
    c.drawString(50, y_pos - 30, form_data.get('manager-name', ''))
    
    # Manager signature
    c.setFont("Helvetica-Bold", 9)
    c.drawString(220, y_pos, "Department Manager's Signature")
    c.drawString(220, y_pos - 15, "Firma del Gerente")
    c.line(220, y_pos - 30, 370, y_pos - 30)
    c.setFont("Helvetica", 9)
    c.drawString(220, y_pos - 45, form_data.get('manager-signature', ''))
    
    # Date
    c.setFont("Helvetica-Bold", 9)
    c.drawString(390, y_pos, "Date")
    c.drawString(390, y_pos - 15, "Fecha")
    c.line(390, y_pos - 30, 540, y_pos - 30)
    c.setFont("Helvetica", 9)
    c.drawString(390, y_pos - 45, form_data.get('manager-date', ''))
    
    c.save()
    return temp_file.name

def generate_mileage_pdf(form_data):
    try:
        # Create a temporary file to store the PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Create a simple PDF document
        c = canvas.Canvas(temp_file_path, pagesize=letter)
        width, height = letter
        
        # Add title
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height-50, "MERIT ALUMINUM")
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, height-70, "MILEAGE REIMBURSEMENT REPORT")
        
        # Add employee information
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, height-100, "Employee: " + form_data.get('employee-name', ''))
        c.drawString(50, height-120, "Branch: " + form_data.get('branch', ''))
        c.drawString(50, height-140, "Week Ending: " + form_data.get('week-ending', ''))
        
        # Add total miles and amount
        c.drawString(50, height-180, "Total Business Miles: " + form_data.get('total-business-miles', '0'))
        c.drawString(50, height-200, "Reimbursement Rate: $0.70 per mile")
        c.drawString(50, height-220, "Total Amount: $" + form_data.get('total-amount', '0'))
        
        # Add signature information
        c.drawString(50, height-260, "Employee Signature: " + form_data.get('employee-signature', ''))
        c.drawString(50, height-280, "Approved By: " + form_data.get('approved-by', ''))
        c.drawString(50, height-300, "Date: " + form_data.get('approval-date', ''))
        
        # Save the PDF
        c.save()
        return temp_file_path
    except Exception as e:
        print(f"Error in PDF generation: {str(e)}")
        # Create a very simple PDF as fallback
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file_path = temp_file.name
        temp_file.close()
        
        c = canvas.Canvas(temp_file_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 700, "MILEAGE REPORT")
        c.setFont("Helvetica", 12)
        c.drawString(100, 680, "Employee: " + form_data.get('employee-name', ''))
        c.save()
        return temp_file_path

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate them with the updated schema
        db.drop_all()
        db.create_all()
        print("Database tables created with updated schema")
            
    app.run(debug=True)
