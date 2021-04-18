from flask import Flask, request, Response, jsonify
from app.db_manager import DB_Manager
import boto3, botocore
import sys



app = Flask(__name__)
db = DB_Manager()
s3 = boto3.client('s3', aws_access_key_id='AKIAQQORPAYKZH4ZPNG4',
   aws_secret_access_key='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')

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
@app.route('/register', methods=['GET', 'POST'])
def submit_reg():
    bucket_name = 'rhdbucket'
    token = request.json['token']
    valid, user = db.validate_token(token)
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
             'alternate_phone']

    reg_info = build_info(request.json, mandatory_items, optional_items)
    if not reg_info:
        return Response(status=402)
    reg_info['id'] = db.gen_id()
    reg_info['submitted_by'] = user


    headshot = request.files['headshot']
    reg_info["headshot_url"] = None
    reg_info["consent_url"] = None
    reg_info["pcn_consent_url"] = None
    filename = f'{reg_info["id"]}_headshot.jpg'
    if headshot.filename != '':
        try:
            s3.upload_fileobj(
                headshot,
                bucket_name,
                filename,
                ExtraArgs={'ACL':'public-read'}
            )
            reg_info["headshot_url"] = f'https://rhdbucket.s3.us-east-2.amazonaws.com/{filename}'.jsonat(headshot.filename)

        except Exception as e:
            print("Error uploading headshot: ", e)
            return e
    if 'consent' in request.files:
        consent = request.files['consent']
        filename = f'{reg_info["id"]}_consent.jpg'
        if consent.filename != '':
            try:
                s3.upload_fileobj(
                    consent,
                    bucket_name,
                    filename,
                    ExtraArgs={'ACL':'public-read'}
                )

            except Exception as e:
                print("Error uploading consent: ", e)
                return e

    if not db.submit_registration(reg_info):
        return Response(status=500)
    return Response(status=200)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.json['username']
    pw = request.json['password']
    token, error = db.login(username, pw)
    if error:
        return Response(status=401)
    return jsonify({'token': token.decode('utf-8')})


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
@app.route('/screening_echo', methods=['GET', 'POST'])
def submit_screening_echo():
    token = request.json['token']
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
             
    reg_info = build_info(request.json, mandatory_items, optional_items)
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


@app.route('/find_patients', methods=['GET', 'POST'])
def find_patient():
    given_items = request.json
    found = db.get_patients(given_items)
    if found:
        return jsonify(found)
    return Response(status=404)

'''
verify that needed items are in a request and build an item for db
params:
    form: request.json
    mandatory_items: items that must be present (list<string>)
    optional_items: items that aren't needed (list<string>)
return:
    an object containing all items to be passed into db
'''
def build_info(form, mandatory_items, optional_items):
    info = {}
    json = form['patient_info']
    sys.stderr.write(str(json))
    sys.stderr.write("\n")
    sys.stderr.write(str(type(json)))
    sys.stderr.flush()
    for item in mandatory_items:
        if item not in json:
            return False
        info[item] = json[item]

    for item in optional_items:
        if item in json:
            info[item] = json[item]
    return info

if __name__ == "__main__":
    app.debug = True
    app.run()