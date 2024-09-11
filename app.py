
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, abort
from pymongo import MongoClient
import datetime
import io
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)

# MongoDB Client Setup
client = MongoClient('mongodb+srv://nithin:nithin@cluster0.ohw9t2m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['shift_handover']
logs_collection = db['logs']

@app.route('/api/latest_alerts')
def latest_alerts():
    # Simulate fetching the latest alerts
    alerts = [
        "Alert: Compliance issue in Area 1",
        "Alert: Safety check overdue in Area 2"
    ]
    return jsonify({'alerts': alerts})

@app.route('/history')
def history():
    logs = list(db.logs.find())
    return render_template('history.html', logs=logs)

@app.route('/')
def l():
  return render_template('login.html')
# Route: Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add your authentication logic here
        if username == "CoalIndia" and password == "CoalIndia":
          return redirect(url_for('dashboard'))
    return render_template('login.html')

# Route: Dashboard Page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route: Shift Log Entry
@app.route('/shift_logs', methods=['GET', 'POST'])
def shift_logs():
    if request.method == 'POST':
        log_data = {
            'start_time': request.form['start_time'],
            'end_time': request.form['end_time'],
            'tasks_completed': request.form['tasks_completed'],
            'red_flags': request.form['red_flags'],
            'no_of_workers': request.form['no_of_workers'],
            'coal_production': request.form['coal_production']
        }
        db.logs.insert_one(log_data)
        return redirect(url_for('shift_logs'))
    logs = list(db.logs.find())
    return render_template('shift_logs.html', logs=logs)

# Route: SMP Entry
@app.route('/smp', methods=['GET', 'POST'])
def smp():
    if request.method == 'POST':
        smp_data = {
            'hazard': request.form['hazard'],
            'control': request.form['control'],
            'monitoring': request.form['monitoring']
        }
        db.smp.insert_one(smp_data)
        return redirect(url_for('smp'))
    return render_template('smp_entry.html')

# Route: Compliance Monitoring Page
@app.route('/compliance_m')
def compliance():
    return render_template('compliance.html')



# Route: Generate PDF Report
@app.route('/generate_report/<log_id>')
def generate_report(log_id):
    # Find the log with the given ID (normally from a database)
    log = logs_collection.find_one({'_id': ObjectId(log_id)})
    
    if not log:
        abort(404, description="Log not found")

    # Create a byte buffer for the PDF
    buffer = BytesIO()

    # Create the PDF object using reportlab
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Set font and size for the PDF content
    p.setFont("Helvetica", 12)

    # Add content to the PDF
    p.drawString(100, height - 100, f"Start Time: {log['start_time']}")
    p.drawString(100, height - 120, f"End Time: {log['end_time']}")
    p.drawString(100, height - 140, f"Tasks Completed: {log['tasks_completed']}")
    p.drawString(100, height - 160, f"Red Flags: {log['red_flags']}")
    p.drawString(100, height - 180, f"No of Workers: {log['no_of_workers']}")
    p.drawString(100, height - 200, f"Coal Produced: {log['coal_production']}")
    p.drawString(100, height - 220, f"Coal: {int(log['coal_production'])*int(log['coal_production'])}")

    # Finish the page
    p.showPage()
    p.save()

    # Move the buffer pointer to the beginning
    buffer.seek(0)

    # Send the file to the client as a downloadable PDF
    return send_file(buffer, as_attachment=True, download_name=f"log_{log_id}_report.pdf", mimetype='application/pdf')

# Route: Filter Logs
@app.route('/filter_logs', methods=['GET'])
def filter_logs():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    query = {}
    if start_time:
        query['start_time'] = {'$gte': start_time}
    if end_time:
        query['end_time'] = {'$lte': end_time}

    logs = list(db.logs.find(query))

    for log in logs:
        log['_id'] = str(log['_id'])

    return jsonify(logs)


@app.route('/logout')
def logout():
    return redirect(url_for('login'))

# Main entry point
if __name__ == '_main_':
    app.run(debug=True)