import ssl
from xmlrpc.client import ServerProxy, Fault
from flask import Flask, g, session, redirect, url_for, request, render_template, render_template_string, flash

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8zJijhde7382idjd]/'

def get_client():
    if not hasattr(g, 'client'):
        #context = ssl.create_default_context()
        context = ssl._create_unverified_context()
        g.client = ServerProxy("https://%s/rpc/api" % (session['hostname']), context=context)
    return g.client

def get_name(sid):
    # {'name': 'guest1.zypp.lo', 'id': 1000010011, 'last_checkin': <DateTime '20200114T23:00:13' at 0x7f821ffe5400>}
    client = get_client()
    try:
        return client.system.getName(session['key'], sid)['name']
    except Fault as err:
        flash("Erreur API : %s" % err.faultString)
        return None

def list_groups(sid):
    client = get_client()
    try:
        test = client.system.list_groups(session['key'], sid)
        return test
    except Fault as err:
        flash("Erreur API : %s" % err.faultString)
        return None

@app.route('/')
def index():
    if ('username' or 'password' or 'hostname') not in session:
        return redirect(url_for('login'))
    client = get_client()
    try:
        score = client.system.get_system_currency_scores(session['key'])
        groups = client.systemgroup.listAllGroups(session['key'])
    except Fault as err:
        flash("Erreur API : %s" % err.faultString)
        session.pop('username', None)
        return redirect(url_for('login'))
    for i in range( len(score) ):
        score[i]["name"] = get_name(score[i]["sid"])
    for i in range( len(score) ):
        score[i]["groups"] = list_groups(score[i]["sid"])
    selected_group=request.args.get('selected_group')
    selected_sid = 0
    name = ""
    if request.args.get('selected_sid') != None:
        selected_sid = int(request.args.get('selected_sid'))
        name = get_name(selected_sid)
    patches=[]
    if selected_sid != 0:
        patches=client.system.getRelevantErrata(session['key'],selected_sid)
    return render_template('system_currency.html', score=score, groups=groups, selected_group=selected_group,selected_sid=selected_sid,patches=patches,name=name)

@app.route('/scans')
def scans():
    if ('username' or 'password' or 'hostname') not in session:
        return redirect(url_for('login'))
    client = get_client()
    scans = []
    try:
        for system in client.system.list_systems(session['key']):
            actions = []
            sys_name = get_name(system['id'])
            for scan in client.system.scap.list_xccdf_scans(session['key'], system["id"]):
                detail = client.system.scap.get_xccdf_scan_details(session['key'], scan['xid'])
                actions.append({'date': detail['start_time'].value, 'action_id': detail['action_id']})
            scans.append({'name': sys_name, 'sid': system["id"], 'actions': actions})
        return render_template('scans.html', scans=scans)
    except Fault as err:
        flash("Erreur API : %s" % err.faultString)
        session.pop('username', None)
        return redirect(url_for('login'))

@app.route('/cve')
def cve():
    if ('username' or 'password' or 'hostname') not in session:
        return redirect(url_for('login'))
    client = get_client()
    cve = []
    try:
        if request.args.get('input_cve') != None:
            selected_cve=request.args.get('input_cve')
            for system in client.audit.listSystemsByPatchStatus(session['key'],selected_cve):
                system['hostname'] = client.system.getDetails(session['key'],system['system_id'])['hostname']
                cve.append(system)
    except Fault as err:
        flash("The CVE "+request.args.get('input_cve')+" doesn't exist.")
    try:
#        selected_cve="CVE-2019-20916"
        return render_template('cve.html', cve=cve)
    except Fault as err:
        flash("Erreur API : %s" % err.faultString)
        session.pop('username', None)
        return redirect(url_for('login'))

@app.route('/download/<int:sys_id>/<int:action_id>')
def download(sys_id=None, action_id=None):
    path = "/var/spacewalk/systems/1/%s/actions/%s/report.html" % (sys_id, action_id)
    with open(path, 'r') as content_file:
        content = content_file.read()
        return render_template_string(content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        session['hostname'] = request.form['hostname']

        client = get_client()
        try:
            session['key'] = client.auth.login(session['username'],
                                               session['password'])
        except Fault as err:
            flash("Erreur API : %s" % err.faultString)
            session.pop('username', None)
            return redirect(url_for('login'))
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    flash("Disconnected!")
    session.pop('username', None)
    return redirect(url_for('index'))
