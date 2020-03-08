import re
import sys
import json
import datetime
from application.helpers.logger import get_logger

logger = get_logger('Normalizer', logger_name=__name__)


class JobNormalizer:
    def __init__(self, redis_connection):
        self.job_dict = dict()
        self.list_field = list(set([
            i
            for domain in json.loads(redis_connection.get('job_rules')).values()
            for i in domain
        ]))

    @staticmethod
    def clean_text(_text):
        if _text is None:
            return ''
        _text = re.sub(r'\n+', '\n', _text)
        _text = re.sub(r'\s+', ' ', _text)
        return _text.strip()

    def normalize_salary(self):
        try:
            salary = self.job_dict['salary']
            if salary is None:
                # return -1
                raise Exception('Invalid Salary, This record might not be job. Del this job\n')

            salary = re.sub(r"\s+", ' ', re.sub(r"\n+", '\n', salary.lower()))
            salary = re.sub(r"\(.*\)", '', salary)

            if not re.match(r".*\d.*", salary):
                return -1, -1

            if '-' in salary:
                salary = salary.split('-')[0].strip()

            if ',' in salary:
                salary = salary.replace(',', '')
            else:
                if re.match(r"\.\d{1,2} +", salary):
                    salary = re.sub(r"\.\d{1,2} +", ' ', salary)
                else:
                    salary = salary.replace('.', '')

            if re.match(r'.*triệu.*', salary):
                salary = re.sub(r"[^0-9]+", '', salary)
                return int(salary.strip()) * 1000000, 'VND'

            salary = int(re.sub(r'[^0-9]', '', salary))
            if salary > 100000:
                return salary, 'VND'

            return salary * 23000, 'USD'

        except Exception as ex:
            _, _, lineno = sys.exc_info()
            logger.error('Line error: {} - Error: {}'.format(lineno.tb_lineno, ex))
            raise ex

    def normalize_info(self):
        return self.clean_text(self.job_dict['info'])

    def normalize_deadline_submit(self):
        try:
            deadline_submit = self.clean_text(self.job_dict['deadline_submit'])

            match_date = re.findall(r"\d{1,2}/\d{1,2}/\d{2,4}", deadline_submit)
            if match_date:
                date_to_compare = list()
                for date_str in match_date:
                    splited_date = date_str.split('/')
                    date_to_compare.append(
                        datetime.date(
                            int(splited_date[2]),
                            int(splited_date[1]),
                            int(splited_date[0])
                        )
                    )

                lastest_date = date_to_compare[0]
                for i in date_to_compare:
                    if i > lastest_date:
                        lastest_date = i
                return lastest_date
            return None

        except Exception as ex:
            print('Normalize deadline_submit ERROR - {}'.format(str(ex)))
            return ''

    def normalize_experience(self):
        experience = self.clean_text(self.job_dict['experience'])
        if ':' in experience:
            experience = experience.split(':')[-1].strip()

        if experience == '':
            experience = None

        return experience

    def normalize_title(self):
        return self.clean_text(self.job_dict['title'])

    def normalize_company(self):
        return self.clean_text(self.job_dict['company'])

    def normalize_location(self):
        location = self.clean_text(self.job_dict['location'])
        if ':' in location:
            location = location.split(':')[-1].strip()
        return location

    def normalize_degree_requirements(self):
        degree_requirements = self.clean_text(self.job_dict['degree_requirements'])
        if ':' in degree_requirements:
            degree_requirements = degree_requirements.split(':')[-1].strip()
        if degree_requirements == '':
            degree_requirements = None
        return degree_requirements

    def normalize_no_of_opening(self):
        try:
            no_of_opening = self.clean_text(self.job_dict['no_of_opening'])
            if no_of_opening == '':
                return -1
            if ':' in no_of_opening:
                no_of_opening = no_of_opening.split(':')[-1].strip()

            no_of_opening = int(no_of_opening)

            return no_of_opening
        except:
            return -1

    def normalize_formality(self):
        formality = self.clean_text(self.job_dict['formality'])
        if ':' in formality:
            formality = formality.split(':')[-1].strip()
        return formality

    def normalize_position(self):
        position = self.clean_text(self.job_dict['position'])
        if ':' in position:
            position = position.split(':')[-1].strip()
        return position

    def normalize_gender_requirements(self):
        gender_requirements = self.clean_text(self.job_dict['gender_requirements'])
        if ':' in gender_requirements:
            gender_requirements = gender_requirements.split(':')[-1].strip()
        if gender_requirements == '':
            gender_requirements = None
        return gender_requirements

    def normalize_career(self):
        career = self.clean_text(self.job_dict['career'])
        if ':' in career:
            career = career.split(':')[-1].strip()
        #     if '/' in career:
        #         return [x.strip() for x in career.split('/')]
        #     if '-' in career:
        #         return [x.strip() for x in career.split('-')]
        #     print(career)
        if career == '':
            career = None
        return career

    def normalize_description(self):
        description = self.clean_text(self.job_dict['description'])
        if description == '':
            description = None
        return description

    def normalize_benefit(self):
        benefit = self.clean_text(self.job_dict['benefit'])
        if benefit == '':
            benefit = None
        return benefit

    def normalize_job_requirements(self):
        job_requirements = self.clean_text(self.job_dict['job_requirements'])
        if job_requirements == '':
            job_requirements = None
        return job_requirements

    def normalize_profile_requirements(self):
        profile_requirements = self.clean_text(self.job_dict['profile_requirements'])
        if profile_requirements == '':
            profile_requirements = None
        return profile_requirements

    def normalize_contact(self):
        contact = self.clean_text(self.job_dict['contact'])
        if contact == '':
            contact = None
        return contact

    def normalize_other_info(self):
        other_info = self.clean_text(self.job_dict['other_info'])
        if other_info == '':
            other_info = None
        return other_info

    def run_normalize(self, job_dict):
        try:
            self.job_dict = job_dict
            n_salary, currency_unit = self.normalize_salary()
            ret_dict = {
                'title': self.job_dict['title'],
                'salary_normalize': float(n_salary),
                'currency_unit': currency_unit,
                'salary': self.job_dict['salary'],
                'url': self.job_dict['url'],
                'company': self.normalize_company(),
                'location': self.normalize_location(),
                'info': self.normalize_info(),
                'degree_requirements': self.normalize_degree_requirements(),
                'deadline_submit': self.normalize_deadline_submit(),
                'experience': self.normalize_experience(),
                'no_of_opening': self.normalize_no_of_opening(),
                'formality': self.normalize_formality(),
                'position': self.normalize_position(),
                'gender_requirements': self.normalize_gender_requirements(),
                'career': self.normalize_career(),
                'description': self.normalize_description(),
                'benefit': self.normalize_benefit(),
                'job_requirements': self.normalize_job_requirements(),
                'profile_requirements': self.normalize_profile_requirements(),
                'contact': self.normalize_contact(),
                'other_info': self.normalize_other_info(),
            }
            return ret_dict
        except Exception as ex:
            _, _, lineno = sys.exc_info()
            logger.error('Line error: {} - Error: {}'.format(lineno.tb_lineno, ex))
            raise ex


class CandidateNormalizer:
    def __init__(self, redis_connection):
        self.candidate_dict = dict()
        self.normalizable = {
            method_name: getattr(self, method_name) for method_name in dir(self)
            if callable(getattr(self, method_name)) and method_name.startswith('normalize_candidate')
        }
        self.redis_connection = redis_connection
        self.list_field = list(set([
            i
            for domain in json.loads(redis_connection.get('candidate_rules')).values()
            for i in domain
        ]))

    @staticmethod
    def clean_text(_text):
        if _text is None:
            return ''
        _text = re.sub(r'\n+', '\n', _text)
        _text = re.sub(r'\s+', ' ', _text)
        return _text.strip()

    def normalize_candidate_title(self):
        _title = self.candidate_dict['title']
        _title = self.clean_text(_title)

        return _title

    def normalize_candidate_name(self):
        _name = self.candidate_dict['name']
        _name = self.clean_text(_name)

        return _name

    def normalize_candidate_expected_salary(self):
        _expected_salary = self.candidate_dict['expected_salary']
        _expected_salary = self.clean_text(_expected_salary)

        return _expected_salary

    def normalize_candidate_expected_location(self):
        _expected_location = self.candidate_dict['expected_location']
        _expected_location = self.clean_text(_expected_location)

        return _expected_location

    def normalize_candidate_date_created(self):
        _date_created = self.candidate_dict['date_created']
        _date_created = self.clean_text(_date_created)

        return _date_created

    def normalize_candidate_phone_number(self):
        _phone_number = self.candidate_dict['phone_number']
        _phone_number = self.clean_text(_phone_number)

        return _phone_number

    def normalize_candidate_info(self):
        _info = self.candidate_dict['info']
        _info = self.clean_text(_info)

        return _info

    def normalize_candidate_url(self):
        _url = self.candidate_dict['url']
        _url = self.clean_text(_url)

        return _url

    def normalize_candidate_payment_forms(self):
        _payment_forms = self.candidate_dict['payment_forms']
        _payment_forms = self.clean_text(_payment_forms)

        return _payment_forms

    def normalize_candidate_type_of_employment(self):
        _type_of_employment = self.candidate_dict['type_of_employment']
        _type_of_employment = self.clean_text(_type_of_employment)

        return _type_of_employment

    def normalize_candidate_experience(self):
        _experience = self.candidate_dict['experience']
        _experience = self.clean_text(_experience)

        return _experience

    def normalize_candidate_age(self):
        _age = self.candidate_dict['age']
        _age = self.clean_text(_age)

        return _age

    def normalize_candidate_gender(self):
        _gender = self.candidate_dict['gender']
        _gender = self.clean_text(_gender)

        return _gender

    def normalize_candidate_email(self):
        _email = self.candidate_dict['email']
        _email = self.clean_text(_email)

        return _email

    def normalize_candidate_academic_level(self):
        _academic_level = self.candidate_dict['academic_level']
        _academic_level = self.clean_text(_academic_level)

        return _academic_level

    def normalize_candidate_major(self):
        _major = self.candidate_dict['major']
        _major = self.clean_text(_major)

        return _major

    def normalize_candidate_school(self):
        _school = self.candidate_dict['school']
        _school = self.clean_text(_school)

        return _school

    def normalize_candidate_language(self):
        _language = self.candidate_dict['language']
        _language = self.clean_text(_language)

        return _language

    def normalize_candidate_computer_skill(self):
        _computer_skill = self.candidate_dict['computer_skill']
        _computer_skill = self.clean_text(_computer_skill)

        return _computer_skill

    def normalize_candidate_degree_certificate(self):
        _degree_certificate = self.candidate_dict['degree_certificate']
        _degree_certificate = self.clean_text(_degree_certificate)

        return _degree_certificate

    def normalize_candidate_year_of_experience(self):
        _year_of_experience = self.candidate_dict['year_of_experience']
        _year_of_experience = self.clean_text(_year_of_experience)

        return _year_of_experience

    def normalize_candidate_other_skill(self):
        _other_skill = self.candidate_dict['other_skill']
        _other_skill = self.clean_text(_other_skill)

        return _other_skill

    def normalize_candidate_expected_work(self):
        _expected_work = self.candidate_dict['expected_work']
        _expected_work = self.clean_text(_expected_work)

        return _expected_work

    def normalize_candidate_expected_level(self):
        _expected_level = self.candidate_dict['expected_level']
        _expected_level = self.clean_text(_expected_level)

        return _expected_level

    def normalize_candidate_expected_career(self):
        _expected_career = self.candidate_dict['expected_career']
        _expected_career = self.clean_text(_expected_career)

        return _expected_career

    def normalize_candidate_expected_goals(self):
        _expected_goals = self.candidate_dict['expected_goals']
        _expected_goals = self.clean_text(_expected_goals)

        return _expected_goals

    def normalize_candidate_birthday(self):
        _birthday = self.candidate_dict['birthday']
        _birthday = self.clean_text(_birthday)

        return _birthday

    def normalize_candidate_marital_status(self):
        _marital_status = self.candidate_dict['marital_status']
        _marital_status = self.clean_text(_marital_status)

        return _marital_status

    def normalize_candidate_career(self):
        _career = self.candidate_dict['career']
        _career = self.clean_text(_career)

        return _career

    def run_normalize(self, candidate_dict):
        self.candidate_dict = candidate_dict
        ret_dict = dict()
        for _field in self.list_field:
            if _field not in self.candidate_dict:
                ret_dict[_field] = ''
            elif 'normalize_candidate_' + _field in self.normalizable:
                ret_dict[_field] = self.normalizable['normalize_candidate_' + _field]()
            else:
                ret_dict[_field] = self.candidate_dict[_field]

        return ret_dict


class BdsNormalizer:
    def __init__(self, redis_connection):
        self.bds_dict = dict()
        self.list_field = list(set([
            i
            for domain in json.loads(redis_connection.get('candidate_rules')).values()
            for i in domain
        ]))

    def run_normalize(self, bds_dict):
        self.bds_dict = bds_dict

        return self. bds_dict
