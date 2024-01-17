from flask import Flask, render_template, request, jsonify, redirect, url_for
import threading
import time
import os
from colorama import Fore

print(f"{Fore.GREEN}Started{Fore.WHITE}")

app = Flask(__name__)

pilots = {}
controllers = {}
controller_ips = []




# Hardcoded admin credentials for simplicity
admin_username = 'rysio12'
admin_password = 'Polska007'

@app.route('/admin', methods=['GET', 'POST'])
def admin():
      error_message = None  # Initialize error_message here

      if request.method == 'POST':
          username = request.form.get('username')
          password = request.form.get('password')

          if username == admin_username and password == admin_password:
              # Redirect to the admin dashboard or perform admin actions
              return redirect(url_for('admin_dashboard'))
          else:
              error_message = "Invalid username or password. Please try again."

      return render_template('admin_login.html', error_message=error_message)








def update_controllers():
    while True:
        time.sleep(5)

        for ip in controller_ips:
            if ip in controllers:
                controllers[ip].send(jsonify(pilots).json.encode())

def handle_pilot_update(callsign, gate, frequency, squawk):
    pilots[callsign]['gate'] = gate
    pilots[callsign]['frequency'] = frequency
    pilots[callsign]['squawk'] = squawk

def remove_pilot(callsign):
    if callsign in pilots:
        del pilots[callsign]
        print(f"{Fore.GREEN}Pilot {callsign} removed{Fore.WHITE}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pilot/login', methods=['GET', 'POST'])
def pilot_login():
    if request.method == 'POST':
        callsign = request.form.get('callsign', type=str)
        aircraft = request.form.get('aircraft', type=str)
        flightrules = request.form.get('flightrules', type=str)
        arrival = request.form.get('arrival', type=str)
        departure = request.form.get('departure', type=str)
        route = request.form.get('route', type=str)
        initial = request.form.get('initial', type=str)
        cruise = request.form.get('cruise', type=str)
        gate = request.form.get('gate', type=str)
          

        if callsign:
            pilots[callsign] = {'aircraft': aircraft, 'flightrules': flightrules, 'arrival': arrival, 'departure': departure, 'frequency': '', 'squawk': '', 'initial': initial, 'cruise': cruise, 'gate': gate}
            print(f"{Fore.GREEN}Pilot {callsign} logged in{Fore.WHITE}")
            return redirect(url_for('pilot_page', callsign=callsign))
          
    return render_template('pilot_login.html')

@app.route('/controller/login', methods=['GET', 'POST'])
def controller_login():
    if request.method == 'POST':
        print()
        callsign = request.form.get('callsign', type=str)
        frequency = request.form.get('frequency', type=str)

        if callsign:
            controllers[request.environ['REMOTE_ADDR']] = {'callsign': callsign, 'frequency': frequency}
            controller_ips.append(request.environ['REMOTE_ADDR'])
            return redirect(url_for('controller_page', callsign=callsign))

    return render_template('controller_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
      #def controller_page(callsign):
  print(f"{Fore.GREEN}Admin Page {Fore.WHITE}")
  if request.method == 'POST':
      print(f"{Fore.GREEN}Admin Page Post")
      if 'remove' in request.form:
          callsign_to_remove = request.form.get('remove_callsign', type=str)
          remove_pilot(callsign_to_remove)
          return redirect(url_for('controller_page'))

  return render_template('admin_dashboard.html', pilots=pilots)

@app.route('/pilot/<callsign>', methods=['GET', 'POST'])
def pilot_page(callsign):
    if request.method == 'POST':
        gate = request.form.get('gate', type=str)
        frequency = request.form.get('frequency', type=str)
        squawk = request.form.get('squawk', type=str)

        if 'remove' in request.form:
            remove_pilot(callsign)
            return redirect(url_for('index'))

        if callsign in pilots:
            handle_pilot_update(callsign, gate, frequency, squawk)

    return render_template('pilot_page.html', callsign=callsign, pilot=pilots[callsign])

@app.route('/controller/<callsign>', methods=['GET', 'POST'])
def controller_page(callsign):
    print(f"{Fore.GREEN}Controller Page {Fore.WHITE}")
    if request.method == 'POST':
        print(f"{Fore.GREEN}Controller Page Post")
        if 'remove' in request.form:
            callsign_to_remove = request.form.get('remove_callsign', type=str)
            remove_pilot(callsign_to_remove)
            return redirect(url_for('controller_page', callsign=callsign))

    return render_template('controller_page.html', callsign=callsign, pilots=pilots)

if __name__ == '__main__':
    update_thread = threading.Thread(target=update_controllers)
    update_thread.start()

    print(f"{Fore.GREEN}Started Flask{Fore.WHITE}")
  
    app.run(host='0.0.0.0', debug=True, port=int(os.getenv("WEB_PORT", 5000, )))
