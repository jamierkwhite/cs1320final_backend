from flask import Flask, request, Response, jsonify
from app.db_manager import DB_Manager
import json


app = Flask(__name__)
db = DB_Manager()


@app.route('/')
def default():
    return 'this is the backend for the screening app'


'''
route to submit a new registration. available at /register
required: first_name
          last_name
          birth_date
          age
          school_name
          standard
          village
          sub_county
          church
          childrens_Home
          care_taker
          father
          mother
          care_taker_phone
          alternate_phone
returns: a new generated id
'''
@app.route('/register', methods=['POST'])
def submit_reg():
    token = request.form['token']
    valid, user = db.validate_tokenverify_token(token)
    if not valid:
        return Response(status=401)
    mandatory_items = ['first_name', 'last_name']
    optional_items = [
             'birth_date',
             'age',
             'school_name',
             'standard',
             'village',
             'sub_county',
             'church',
             'childrens_Home',
             'care_taker',
             'father',
             'mother',
             'care_taker_phone',
             'alternate_phone',
             'headshot_url',
             'consent_url',
             'pcn_consent_url']
    reg_info = build_info(request.form, mandatory_items, optional_items)
    if not reg_info:
        return Response(status=402)
    reg_info['id'] = db.gen_id()
    reg_info['submitted_by'] = user
    if not db.submit_registration(reg_info):
        return Response(status=500)
    return Response(status=200)
    

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    pw = request.form['password']
    token, error = db.login(username, pw)
    if error:
        return Response(status=401)
    return Response(response=json.dumps({'token':token}), status=200)


'''
route to recieve screening echo info available at /screening_echo
required: id
          date
          location
          am_valve_leaflet_thickness_normality
          pm_valve_leaflet_thickness_normality
          pm_valve_mobility_normality
          a_valve_thickness_normality
          m_valve_function_normality
          a_valve_function_normality
          am_valve_leaflet_mobility_normality
          mitral_regurgitation
          aortic_regurgitation
          comments
'''
@app.route('/screening_echo', methods=['POST'])
def submit_screening_echo():
    token = request.form['token']
    valid, user = db.validate_tokenverify_token(token)
    if not valid:
        return Response(status=401)
    mandatory_items = [ 'id',
                        'date',
                        'location',
                        'am_valve_leaflet_thickness_normality',
                        'pm_valve_leaflet_thickness_normality',
                        'pm_valve_mobility_normality',
                        'a_valve_thickness_normality',
                        'm_valve_function_normality',
                        'a_valve_function_normality',
                        'am_valve_leaflet_mobility_normality',
                        'mitral_regurgitation',
                        'aortic_regurgitation']
    optional_items = ['comments']
             
    reg_info = build_info(request.form, mandatory_items, optional_items)
    if not reg_info:
        return Response(status=402)
    reg_info['submitted_by'] = user
    if not db.submit_screening_echo(reg_info):
        return Response(status=500)
    return Response(status=200)

@app.route('/favicon.ico', methods=['GET'])
def icon():
    return Response(status=404)


def submit_screening_questions():
    return Response(status=501)


@app.route('/find_patients', methods=['POST'])
def find_patient():
    given_items = request.form
    found = db.get_patients(given_items)
    if found:
        return jsonify(found)
    return Response(status=404)

'''
verify that needed items are in a request and build an item for db
params:
    form: request.form
    mandatory_items: items that must be present (list<string>)
    optional_items: items that aren't needed (list<string>)
return:
    an object containing all items to be passed into db
'''
def build_info(form, mandatory_items, optional_items):
    info = {}

    for item in mandatory_items:
        if item not in form:
            return False
        info[item] = form[item]

    for item in optional_items:
        if item in form:
            info[item] = form[item]
    return info

if __name__ == "__main__":
    app.debug = True
    app.run()