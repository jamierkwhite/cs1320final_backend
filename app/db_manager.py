import psycopg2
import os
import random
import hashlib
import datetime
import hashlib
import base64

'''
Class to interface with the database
'''
class DB_Manager:
    '''
    instantiate postgres connection and tables
    '''

    def __init__(self):
        DATABASE_URL = os.environ['DATABASE_URL']
        self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        self.cursor = self.conn.cursor()
    
        query = '''CREATE TABLE IF NOT EXISTS Registration(
            id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            birth_date DATE,
            age int,
            school_name TEXT,
            standard decimal,
            village TEXT,
            sub_county TEXT,
            church TEXT,
            childrens_Home TEXT,
            care_taker TEXT,
            father TEXT,
            mother TEXT,
            care_taker_phone VARCHAR(14),
            alternate_phone VARCHAR(14),
            headshot_url TEXT,
            consent_url TEXT,
            pcn_consene_url TEXT,
            submitted_by TEXT)'''
        self.cursor.execute(query)

        query = '''CREATE TABLE IF NOT EXISTS Screening(
            id TEXT PRIMARY KEY,
            date TIMESTAMP,
            location TEXT,
            am_valve_leaflet_thickness_normality BOOL,
            pm_valve_leaflet_thickness_normality BOOL,
            pm_valve_mobility_normality BOOL,
            a_valve_thickness_normality BOOL,
            m_valve_function_normality BOOL,
            a_valve_function_normality BOOL,
            am_valve_leaflet_mobility_normality BOOL,
            mitral_regurgitation FLOAT,
            aortic_regurgitation BOOL,
            comments TEXT,
            submitted_by TEXT,
            FOREIGN KEY (id) REFERENCES Registration(id))'''
        self.cursor.execute(query)

        query = '''CREATE TABLE IF NOT EXISTS PCN(
            id TEXT PRIMARY KEY,
            date TIMESTAMP,
            location TEXT,
            worsening_exercise_intolerance BOOL,
            poor_pcn_reaction BOOL,
            injection_given BOOL,
            comments TEXT,
            submitted_by TEXT,
            FOREIGN KEY (id) REFERENCES Registration(id))'''        
        self.cursor.execute(query)


        query = """CREATE TABLE IF NOT EXISTS users(
            userID TEXT PRIMARY KEY,
            pwHash TEXT UNIQUE
            )
        """
        self.cursor.execute(query)
        

        query = """CREATE TABLE IF NOT EXISTS sessions(
            sessionID TEXT PRIMARY KEY,
            userID TEXT,
            expiration TEXT,
            FOREIGN KEY (userID)
                REFERENCES users(userID)
                    ON DELETE CASCADE
                    ON UPDATE RESTRICT
        )
        """    
        self.cursor.execute(query)
        self.conn.commit()

        


    '''
    method to insert a new registrant into the database
    params:
        reg_info: a dict of registrant attribute name: value
    return: boolean for success
    '''
    def submit_registration(self, reg_info):
        query = '''INSERT INTO Registration
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        try:
            self.cursor.execute(query, 
                (reg_info["id"],
                reg_info["first_name"],
                reg_info["last_name"],
                reg_info["birth_date"],
                reg_info["age"],
                reg_info["school_name"],
                reg_info["standard"],
                reg_info["village"],
                reg_info["sub_county"],
                reg_info["church"],
                reg_info["childrens_Home"],
                reg_info["care_taker"],
                reg_info["father"],
                reg_info["mother"],
                reg_info["care_taker_phone"],
                reg_info["alternate_phone"],
                reg_info["headshot_url"],
                reg_info["consent_url"],
                reg_info["pcn_consent_url"],
                reg_info["submitted_by"]))
            self.conn.commit()
            return True
        except Exception as err:
            print("Exception occured in db_manager.submit_registration: ", err)
            return False


    '''
    method to insert screening questions into the database
    params:
        screening_info: a dict of registrant attribute name: value
    return: boolean for success
    '''
    def submit_screening_echo(self, screening_echo):
        query = '''INSERT INTO Registration
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        try:
            self.cursor.execute(query, 
                (screening_echo['id'],
                 screening_echo['date'],
                 screening_echo['location'],
                 screening_echo['am_valve_leaflet_thickness_normality'],
                 screening_echo['pm_valve_leaflet_thickness_normality'],
                 screening_echo['pm_valve_mobility_normality'],
                 screening_echo['a_valve_thickness_normality'],
                 screening_echo['m_valve_function_normality'],
                 screening_echo['a_valve_function_normality'],
                 screening_echo['am_valve_leaflet_mobility_normality'],
                 screening_echo['mitral_regurgitation'],
                 screening_echo['aortic_regurgitation'],
                 screening_echo['comments'],
                 screening_echo['submitted_by']))
            self.conn.commit()
            return True
        except Exception:
            print("Exception occured in db_manager.submit_screening_echo")
            return False


    
    '''
    create a new ID to be used in the database
    '''
    def gen_id(self, id_length=7):
        #numbers and capital letters that aren't simmilar looking
        usable_characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                             'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K',
                             'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                             'W', 'X', 'Y', 'Z']
        while True:
            new_id = ''
            for _ in range(id_length):
                new_id += usable_characters[int(random.random()*len(usable_characters))]

            q = "SELECT id FROM Registration WHERE id=%s"
            self.cursor.execute(q, (new_id, ))
            results = self.cursor.fetchall()
            if len(results) == 0:
                return new_id
            
    
    def get_patients(self, given_info):
        fields = [
            'id',
            'first_name',
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

        results = set()

        for key in fields:
            if key in given_info:
                val = given_info[key]
                query = 'SELECT FROM registration WHERE %s=%s'
                self.cursor.execute(query, key, val) 
                results = results.intersection(self.cursor.fetchall())
                if len(results) <= 5 and len(results) > 0:
                    return results
        return False
    
    
    def validate_token(self, token):
        is_valid = False
        userID = ""
        q = "SELECT * FROM sessions WHERE sessionID=%s"
        try:
            hashed_token = get_hashed_token(token)
            self.cursor.execute(q, (hashed_token,))
            result = self.cursor.fetchone()
            if (result == None):
                return False, ""
            else:
                expiration = datetime.datetime.strptime(
                    result[2], '%Y-%m-%d %H:%M:%S.%f')
                now = datetime.datetime.now()
                userID = result[1]
                if (expiration > now):
                    return True, userID

        except:
            return False, ""
        return is_valid, userID


    # Logs a client into the Dropbox system.
    #
    # Expected input: userID, password (in plaintext)
    # Expected output: token, err
    def login(self, userID, password):
        error = ""
        token = ""
        q = "SELECT userID,pwHash FROM users WHERE userID=%s"
        try:
            self.cursor.execute(q, (userID,))
            result = self.cursor.fetchone()
            if (result == None):
                return token, "Could not find your Dropbox account."
            processed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()
            pwHash = result[1]
            if processed_pw == pwHash:
                # generate a new sessionID token - see README for citation
                token = base64.b64encode(os.urandom(16))
                # hash the token before storing it in the db
                sessionID = hashlib.sha256(token).hexdigest()
                # set an expiration of the session to be 30 minutes from now
                # see README for citation
                now = datetime.datetime.now()
                now_plus_30 = str(now + datetime.timedelta(minutes=240))
                q = "INSERT INTO sessions (sessionID, userID, expiration) VALUES(%s,%s,%s)"
                self.cursor.execute(q, (sessionID, userID, now_plus_30))
                self.conn.commit()
            else:
                error = "Could not find your Dropbox account."
        except:
            error = "There was an error logging in. Please try again."
        return token, error


    def close(self):
        self.conn.close()

# hashes a token
#
# Expected input:
#   token: token to be hashed
# Expected output: hash(token)
def get_hashed_token(token):
    encoded_token = str(token).encode()
    return hashlib.sha256(encoded_token).hexdigest()


if __name__ == '__main__':
    db = DB_Manager()
    print(db.login('developer', 'C8FZXqr9bIlMFvL2'))
    
    