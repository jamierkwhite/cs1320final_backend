import psycopg2
import random

'''
Class to interface with the database
'''
class DB_Manager:
    '''
    instantiate postgres connection and tables
    '''

    def __init__(self):
        self.conn = psycopg2.connect(database='scappdb',
                    user='postgres',
                    password='jvjye4b66k9ermx7',
                    host='localhost',
                    port='5432')

        self.cursor = self.conn.cursor()

        query = '''CREATE TABLE IF NOT EXISTS Registration(
            id INT PRIMARY KEY,
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
            alternate_phone VARCHAR(14))'''
        self.cursor.execute(query)
        self.conn.commit()

        query = '''CREATE TABLE IF NOT EXISTS Screening(
            id INT PRIMARY KEY,
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
            FOREIGN KEY (id) REFERENCES Registration(id))'''
        self.cursor.execute(query)
        self.conn.commit()

        query = '''CREATE TABLE IF NOT EXISTS PCN(
            id INT PRIMARY KEY,
            date TIMESTAMP,
            location TEXT,
            worsening_exercise_intolerance BOOL,
            poor_pcn_reaction BOOL,
            injection_given BOOL,
            comments TEXT,
            FOREIGN KEY (id) REFERENCES Registration(id))'''        
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
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        try:
            self.cursor.execute(query, 
                reg_info["id"], (
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
                reg_info["pcn_consent_url"]))
            self.conn.commit()
            return True
        except Exception:
            print("Exception occured in db_manager.submit_registration")
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
                 screening_echo['comments']))
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
            id = ''
            for _ in range(id_length):
                id += usable_characters[int(random.random()*len(usable_characters))]

            q = "SELECT id FROM Registration id = %s"
            self.cursor.execute(q, id)
            results = self.cursor.fetchall()
            if len(results) == 0:
                return id
            

    def close(self):
        self.conn.close()


if __name__ == '__main__':
    db = DB_Manager()
    
    