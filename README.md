# GruntCode Invoice System

A modern, dark-themed invoice management system with PDF generation and email capabilities.

## Features

- Create and send professional invoices with custom logo
- Generate PDF invoices automatically
- Email invoices directly to clients
- Track invoice status (Pending, Paid, Overdue, Cancelled)
- Modern dark UI with cyberpunk-inspired design

## Setup Instructions

### Backend Setup

1. Create a virtual environment:

```bash
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure email settings:

- Rename `.env.example` to `.env`
- Update EMAIL_USER and EMAIL_PASS with your Gmail credentials
- **Important:** Update the default email recipient in `app.py` by searching for "default_recipient" and changing it to your desired email address
- For Gmail, you'll need to generate an App Password:
  - Go to Google Account Settings > Security
  - Enable 2-Step Verification
  - Generate App Password for mail

### Frontend Setup

1. Navigate to frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

## Running the Application

1. Start the Flask application (which serves both backend and frontend):

```bash
python app.py
```

2. Access the application at `http://127.0.0.1:5000`

**Note:** While the project includes a React frontend in the `/frontend` directory, the current implementation uses Flask to serve static files for the frontend. The React components have been pre-built and are served directly by the Flask application.

## Usage

1. Create Invoice:

   - Upload your company logo
   - Enter client details
   - Add invoice items
   - Click "Generate & Send Invoice"

2. Track Invoices:

   - View all invoices
   - Update invoice status
   - Monitor payment status
