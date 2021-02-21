from flask import Flask, jsonify, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import re, pycurl, requests, json
from io import BytesIO 
from datetime import datetime
from meraki_sdk.meraki_sdk_client import MerakiSdkClient
from meraki_sdk.exceptions.api_exception import APIException
from creds import meraki_key, dburl, meraki_org_id, meraki_network_reading

x_cisco_meraki_api_key = meraki_key

meraki = MerakiSdkClient(x_cisco_meraki_api_key)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = dburl
db = SQLAlchemy(app)

class RouterNode(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  node = db.Column(db.String(100), nullable=False)
  address = db.Column(db.Text, nullable=False)
  vendor = db.Column(db.String(20), nullable=False, default="Vendor Unknown")
  date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  def __repr__(self):
    return 'Router node ' + str(self.id)

all_routers = [
  {
    'node': 'R1',
    'address': '10.0.0.1',
    'vendor': ''
  },
  {
    'node': 'R2',
    'address': '20.0.0.1',
    'vendor': 'Cisco'
  }


]



@app.route('/')
def index():
  return render_template('index.html')

@app.route('/meraki')
def merakiapi():
  orgs = meraki.organizations.get_organizations()
  return render_template('meraki.html', orgs=orgs)
  #return jsonify(orgs)

@app.route('/meraki/login')
def merakilogin():
  r = requests.get('https://dashboard.meraki.com/api/v0/organizations/', headers={'X-Cisco-Meraki-API-Key': x_cisco_meraki_api_key, 'Content-Type': 'application/json'})
  pretty_json = json.loads(r.text)
  pretty_r = json.dumps(pretty_json, indent=2)
  return render_template('meraki.html', orgs=pretty_json)
  #return pretty_r

@app.route('/meraki/networks')
def merakinetworks():
  r = requests.get('https://dashboard.meraki.com/api/v0/organizations/822027/networks', headers={'X-Cisco-Meraki-API-Key': x_cisco_meraki_api_key, 'Content-Type': 'application/json'})
  pretty_json = json.loads(r.text)
  #pretty_r = json.dumps(pretty_json, indent=2)
  pretty_r = json.dumps(pretty_json, sort_keys = True, indent = 4, separators = (',', ': '))
  return render_template('merakinetworks.html', nets=pretty_json)
  #return jsonify(pretty_r)

@app.route('/meraki/firewall')
def merakifirewall():
  r = requests.get('https://dashboard.meraki.com/api/v0/organizations/{{ meraki_org_id }}/networks/N_645140646620834618/l3FirewallRules', headers={'X-Cisco-Meraki-API-Key': x_cisco_meraki_api_key, 'Content-Type': 'application/json'})
  pretty_json = json.loads(r.text)
  #pretty_r = json.dumps(pretty_json, indent=2)
  pretty_r = json.dumps(pretty_json, sort_keys = True, indent = 4, separators = (',', ': '))
  return render_template('merakinetworks.html', fw=pretty_json)
  #return jsonify(pretty_r)

@app.route('/meraki/pf')
def merakiportforward():
  r = requests.get('https://dashboard.meraki.com/api/v0/organizations/822027/networks/N_645140646620834617/portForwardingRules', headers={'X-Cisco-Meraki-API-Key': x_cisco_meraki_api_key, 'Content-Type': 'application/json'})
  pretty_json = json.loads(r.text)
  #pretty_r = json.dumps(pretty_json, indent=2)
  pretty_r = json.dumps(pretty_json, sort_keys = True, indent = 4, separators = (',', ': '))
  return render_template('merakinetworks.html', pf=pretty_json)
  #return jsonify(pretty_json)

@app.route('/routers', methods=['GET', 'POST'])
def inventory():
    all_routers = RouterNode.query.order_by(RouterNode.date_added)
    return render_template('routers.html', routers=all_routers)

@app.route('/routers/new', methods=['GET', 'POST'])
def new_router():
  if request.method == 'POST':
    router_node = request.form['node']
    router_address = request.form['address']
    router_vendor = request.form['vendor']
    new_router = RouterNode(node=router_node, address=router_address, vendor=router_vendor)
    db.session.add(new_router)
    db.session.commit()
  else:
    return render_template('new_router.html')

@app.route('/routers/delete/<int:id>')
def deleterouter(id):
  router = RouterNode.query.get_or_404(id)
  db.session.delete(router)
  db.session.commit()
  return redirect('/routers')

@app.route('/routers/edit/<int:id>', methods=['GET', 'POST'])
def editrouter(id):
  router = RouterNode.query.get_or_404(id)
  if request.method == 'POST':
    router.node = request.form['node']
    router.address = request.form['address']
    router.vendor = request.form['vendor']
    db.session.commit()
    return redirect('/routers')
  else:
    return render_template('edit.html', router=router)

@app.route('/device42')
def device42():
  r = requests.get('https://swaggerdemo.device42.com/api/1.0/suggest_subnet/4/?mask_bits=28','Accept: application/json', 'Authorization: Basic YXBpX3VzZXI6YXAhX3VzZXJfcHIwZA==')
  pretty_json = json.loads(r.text)
  #pretty_r = json.dumps(pretty_json, indent=2)
  pretty_r = json.dumps(pretty_json, sort_keys = True, indent = 4, separators = (',', ': '))
  #return render_template('merakinetworks.html', nets=pretty_json)
  return jsonify(pretty_r)

@app.route('/home')
def hello():
  tvheadend_text = "http://192.168.10.5:9981/playlist/channels.m3u"

  return "Hello world 2! " + "<a href= "  + tvheadend_text + ">Watch TV!</a>"

@app.route('/name/users/<string:name>/posts/<int:id>')
def sayhi(name, id):
  return "Hello, " + name + ", your id is: " + str(id)

@app.route('/onlyget', methods=['GET'])
def get_req():
  return 'You can only get this webpage.'

if __name__=="__main__":
  app.run(debug=True, host='0.0.0.0')
