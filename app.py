from flask import Flask, render_template, request, Response, session, redirect, url_for
from banner_grabber import grab_banner

app = Flask(__name__)
app.secret_key = 'cybersecurity_project_secret_key'

# Simple in-memory user registry for simulation/testing
USER_DB = {
    "admin": "password123" # Default fallback account
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('authenticated') == True:
        return redirect(url_for('home'))
        
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        # Verify credential presence against memory database
        if username in USER_DB and USER_DB[username] == password:
            session['authenticated'] = True
            return redirect(url_for('home'))
        else:
            error = "Invalid credentials. Please verify parameters."
            
    return render_template('login.html', error=error, active_view='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('authenticated') == True:
        return redirect(url_for('home'))
        
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if username in USER_DB:
            error = "Username profile already registered."
        elif password != confirm_password:
            error = "Password inputs mismatch. Try again."
        elif len(password) < 8:
            error = "Password failed criteria checks (Length < 8)."
        else:
            # Commit account metadata to the runtime dict
            USER_DB[username] = password
            session['authenticated'] = True # Log user in immediately on success
            return redirect(url_for('home'))
            
    return render_template('login.html', error=error, active_view='register')

@app.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
        
    parsed_results = []
    target = ""
    
    if request.method == 'POST':
        target = request.form['target'].strip()
        ports_raw = request.form['ports']
        
        try:
            ports_to_scan = [int(p.strip()) for p in ports_raw.split(",")]
            
            raw_report = f"========================================\n"
            raw_report += f"VANGUARD ENUMERATION REPORT FOR: {target}\n"
            raw_report += f"========================================\n\n"
            
            for port in ports_to_scan:
                result = grab_banner(target, port)
                is_error = result.startswith("Error")
                
                parsed_results.append({
                    "port": port,
                    "result": result,
                    "is_error": is_error
                })
                
                raw_report += f"[+] Port {port} (Status: {'Closed/Filtered' if is_error else 'Open'}):\n{result}\n"
                raw_report += f"----------------------------------------\n"
                
            session['latest_report'] = raw_report
            session['latest_target'] = target
            
        except ValueError:
            parsed_results.append({
                "port": "N/A",
                "result": "Error: Invalid port input format.",
                "is_error": True
            })
            
    return render_template('index.html', parsed_results=parsed_results, target=target)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/download')
def download_report():
    if not session.get('authenticated'):
        return Response("Unauthorized", status=401)
    report_content = session.get('latest_report', 'No report available.')
    target_name = session.get('latest_target', 'scan_report')
    return Response(
        report_content,
        mimetype="text/plain",
        headers={"Content-disposition": f"attachment; filename=vanguard_report_{target_name}.txt"}
    )

if __name__ == '__main__':
    app.run(debug=True)