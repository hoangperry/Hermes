import json
import re
import sys
import datetime
from application.helpers.logger import get_logger

logger = get_logger('Normalizer', logger_name=__name__)


def normalize_salary_range(_salary):
    try:
        if _salary is None or _salary == '':
            return {
                'salary_normalized': [-1, -1],
                'currency_unit': -1
            }

        _salary = re.sub(r"\s+", ' ', re.sub(r"\n+", '\n', _salary.lower()))
        _salary = re.sub(r"\(.*\)", '', _salary)

        if not re.match(r".*\d.*", _salary):
            return {
                'salary_normalized': [-1, -1],
                'currency_unit': -1
            }

        if '-' in _salary:
            _salary = [i.strip() for i in _salary.split('-')]
        else:
            _salary = [_salary]

        currency = 'VND'
        for sall in range(_salary.__len__()):
            if ',' in _salary[sall]:
                _salary[sall] = _salary[sall].replace(',', '')
            elif re.match(r"\.\d{1,2} +", _salary[sall]):
                _salary[sall] = re.sub(r"\.\d{1,2} +", ' ', _salary[sall])
            else:
                _salary[sall] = _salary[sall].replace('.', '')

            if re.match(r'.*triệu.*', _salary[sall]):
                _salary[sall] = re.sub(r"[^0-9]+", '', _salary[sall])
                _salary[sall] = int(_salary[sall].strip()) * 1000000
                currency = 'VND'
                continue

            _salary[sall] = int(re.sub(r'[^0-9]', '', _salary[sall]))
            if 100 < _salary[sall] < 100000:
                currency = 'USD'
            elif _salary[sall] < 100:
                _salary[sall] = _salary[sall] * 1000000
        if _salary.__len__() < 2:
            _salary.append(-1)

        return {
            'salary_normalized': _salary,
            'currency_unit': currency
        }

    except Exception as ex:
        _, _, lineno = sys.exc_info()
        try:
            _, _, lineno = sys.exc_info()
            print('Line error: {} - Error: {}'.format(lineno.tb_lineno, ex))
        except:
            print('Cannot get line error - Error{}'.format(ex))


class JobNormalizer:
    def __init__(self, redis_connection):
        self.job_dict = dict()
        self.list_field = list(set([
            i
            for domain in json.loads(redis_connection.get('job_rules')).values()
            for i in domain
        ]))
        self.exchange_rate = {
            'VND': 1,
            'USD': 23000,
        }
        self.normalizable = {
            method_name: getattr(self, method_name)
            for method_name in dir(self)
            if callable(getattr(self, method_name)) and method_name.startswith('normalize_job')
        }

    @staticmethod
    def clean_text(_text):
        if _text is None:
            return ''
        _text = re.sub(r'\n+', '\n', _text)
        _text = re.sub(r'\s+', ' ', _text)
        return _text.strip()

    def normalize_job_salary(self):
        _salary = self.job_dict['salary']
        return normalize_salary_range(self.clean_text(_salary))

    def normalize_job_info(self):
        return self.clean_text(self.job_dict['info'])

    def normalize_job_deadline_submit(self):
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
                return lastest_date.strftime('%d-%b-%Y')
            return None

        except Exception as ex:
            print('Normalize deadline_submit ERROR - {}'.format(str(ex)))
            return None

    def normalize_job_experience(self):
        experience = self.clean_text(self.job_dict['experience'])
        if ':' in experience:
            experience = experience.split(':')[-1].strip()

        if experience == '':
            experience = None

        return experience

    def normalize_job_title(self):
        return self.clean_text(self.job_dict['title'])

    def normalize_job_company(self):
        return self.clean_text(self.job_dict['company'])

    def normalize_job_location(self):
        location = self.clean_text(self.job_dict['location'])
        if ':' in location:
            location = location.split(':')[-1].strip()
        return location

    def normalize_job_degree_requirements(self):
        degree_requirements = self.clean_text(self.job_dict['degree_requirements'])
        if ':' in degree_requirements:
            degree_requirements = degree_requirements.split(':')[-1].strip()
        if degree_requirements == '':
            degree_requirements = None
        return degree_requirements

    def normalize_job_no_of_opening(self):
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

    def normalize_job_formality(self):
        formality = self.clean_text(self.job_dict['formality'])
        if ':' in formality:
            formality = formality.split(':')[-1].strip()
        return formality

    def normalize_job_position(self):
        position = self.clean_text(self.job_dict['position'])
        if ':' in position:
            position = position.split(':')[-1].strip()
        return position

    def normalize_job_gender_requirements(self):
        gender_requirements = self.clean_text(self.job_dict['gender_requirements'])
        if ':' in gender_requirements:
            gender_requirements = gender_requirements.split(':')[-1].strip()
        if gender_requirements == '':
            gender_requirements = None
        return gender_requirements.lower() if gender_requirements is not None else None

    def normalize_job_career(self):
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

    def normalize_job_description(self):
        description = self.clean_text(self.job_dict['description'])
        if description == '':
            description = None
        return description

    def normalize_job_benefit(self):
        benefit = self.clean_text(self.job_dict['benefit'])
        if benefit == '':
            benefit = None
        return benefit

    def normalize_job_requirements(self):
        job_requirements = self.clean_text(self.job_dict['job_requirements'])
        if job_requirements == '':
            job_requirements = None
        return job_requirements

    def normalize_job_profile_requirements(self):
        profile_requirements = self.clean_text(self.job_dict['profile_requirements'])
        if profile_requirements == '':
            profile_requirements = None
        return profile_requirements

    def normalize_job_contact(self):
        contact = self.clean_text(self.job_dict['contact'])
        if contact == '':
            contact = None
        return contact

    def normalize_job_other_info(self):
        other_info = self.clean_text(self.job_dict['other_info'])
        if other_info == '':
            other_info = ''
        else:
            other_info = re.sub(r'  +', ' ', re.sub(r'\n\n+', '\n', other_info)).split('\n')
        return other_info

    def run_normalize(self, job_dict):
        try:
            self.job_dict = job_dict
            ret_dict = {'url': job_dict['url']} if 'url' in job_dict else {'url': ''}

            for _field in self.list_field:
                if _field not in self.job_dict:
                    ret_dict[_field] = ''
                elif 'normalize_job_' + _field in self.normalizable:
                    ret_dict[_field] = self.normalizable['normalize_job_' + _field]()
                else:
                    ret_dict[_field] = self.job_dict[_field]

            ret_dict['currency_unit'] = ret_dict['salary']['currency_unit']
            ret_dict['salary_normalized'] = ret_dict['salary']['salary_normalized']
            ret_dict['salary_raw'] = job_dict['salary']
            ret_dict['salary'] = list()

            for _salary in ret_dict['salary_normalized']:
                _salary_value = _salary * (
                    self.exchange_rate[ret_dict['currency_unit']]
                    if ret_dict['currency_unit'] != -1
                    else 1
                )
                if _salary_value > 0:
                    ret_dict['salary'].append(_salary_value)
                else:
                    ret_dict['salary'].append(-1)

            return ret_dict
        except Exception as ex:
            _, _, lineno = sys.exc_info()
            print('Line error: {} - Error: {}'.format(lineno.tb_lineno, ex))
            logger.error('Line error: {} - Error: {}'.format(lineno.tb_lineno, ex))
            raise ex


class CandidateNormalizer:
    def __init__(self, redis_connection):
        self.exchange_rate = {
            'VND': 1,
            'USD': 23000,
        }
        self.candidate_dict = dict()
        self.normalizable = {
            method_name: getattr(self, method_name)
            for method_name in dir(self)
            if callable(getattr(self, method_name)) and method_name.startswith('normalize_candidate')
        }
        self.list_field = list(set([
            i
            for domain in json.loads(redis_connection.get('candidate_rules')).values()
            for i in domain
        ]))
        self.phone_prefix_dict = {
            '0120': '070',
            '0121': '079',
            '0122': '077',
            '0126': '076',
            '0128': '078',
            '0123': '083',
            '0124': '084',
            '0125': '085',
            '0127': '081',
            '0129': '082',
            '0162': '032',
            '0163': '033',
            '0164': '034',
            '0165': '035',
            '0166': '036',
            '0167': '037',
            '0168': '038',
            '0169': '039',
            '0186': '056',
            '0188': '058',
            '0199': '059',
        }

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

        return _name.capitalize()

    def normalize_candidate_expected_salary(self):
        _expected_salary = self.candidate_dict['expected_salary']
        return normalize_salary_range(self.clean_text(_expected_salary))

    def normalize_candidate_expected_location(self):
        _expected_location = self.candidate_dict['expected_location']
        _expected_location = self.clean_text(_expected_location)

        return _expected_location

    def normalize_candidate_date_created(self):
        if self.candidate_dict['date_created'] is None:
            return None
        _date_created = self.candidate_dict['date_created']
        _date_created = self.clean_text(_date_created)
        match = re.findall(r'^\d{1,2}/\d{1,2}/\d{2,4}$', _date_created)

        if match:
            try:
                date_time_splited = match[0].split('/')
                ret_date = datetime.date(
                    int(date_time_splited[-1]),
                    int(date_time_splited[-2]),
                    int(date_time_splited[-3])
                )
                return ret_date.strftime('%d-%b-%Y')
            except:
                return None

        return None

    def normalize_candidate_phone_number(self):
        if self.candidate_dict['phone_number'] is None:
            return list()
        _phone_numbers = self.candidate_dict['phone_number']
        _phone_numbers = self.clean_text(_phone_numbers)
        _phone_numbers = re.sub(r'[.,-]', '', _phone_numbers)
        _phone_numbers = re.findall(r'\d{8,}', _phone_numbers)

        for _phone in range(_phone_numbers.__len__()):
            _phone_numbers[_phone] = re.sub(r"\D+", "", _phone_numbers[_phone])
            _phone_numbers[_phone] = re.sub(r"(^[+]?84)", "0", _phone_numbers[_phone])
            if _phone_numbers[_phone][0] != "0":
                continue

            _prefix = _phone_numbers[_phone][:4]
            if _prefix in self.phone_prefix_dict:
                _phone_numbers[_phone] = re.sub(
                    _prefix[:4], self.phone_prefix_dict[_prefix], _phone_numbers[_phone]
                )
            if len(_phone_numbers[_phone]) != 10:
                continue

        return _phone_numbers

    def normalize_candidate_info(self):
        _info = self.candidate_dict['info']
        _info = self.clean_text(_info)

        return _info

    def normalize_candidate_payment_forms(self):
        _payment_forms = self.candidate_dict['payment_forms']
        _payment_forms = self.clean_text(_payment_forms)

        return _payment_forms.lower()

    def normalize_candidate_type_of_employment(self):
        _type_of_employment = self.candidate_dict['type_of_employment']
        _type_of_employment = self.clean_text(_type_of_employment)

        return _type_of_employment.lower()

    def normalize_candidate_experience(self):
        _experience = self.candidate_dict['experience']
        _experience = self.clean_text(_experience)

        return _experience

    def normalize_candidate_age(self):
        _age = self.candidate_dict['age']
        _age = self.clean_text(_age)

        if re.match(r'.*\d.*', _age):
            _age = int(re.sub(r'([^\d])+', '', _age))
            if _age > 100:
                return -1
            return _age

        return -1

    def normalize_candidate_gender(self):
        _gender = self.candidate_dict['gender']
        _gender = self.clean_text(_gender)
        _gender = _gender.lower()
        return _gender if _gender in ['nam', 'nữ'] else -1

    def normalize_candidate_email(self):
        _email = self.candidate_dict['email']
        _email = self.clean_text(_email)
        if re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', _email):
            return _email
        return -1

    def normalize_candidate_academic_level(self):
        _academic_level = self.candidate_dict['academic_level']
        _academic_level = self.clean_text(_academic_level)

        return _academic_level.lower()

    def normalize_candidate_major(self):
        _major = self.candidate_dict['major']
        _major = self.clean_text(_major)

        return _major.lower()

    def normalize_candidate_school(self):
        _school = self.candidate_dict['school']
        _school = self.clean_text(_school)

        return _school.capitalize()

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

        return _expected_level.lower()

    def normalize_candidate_expected_career(self):
        _expected_career = self.candidate_dict['expected_career']
        _expected_career = self.clean_text(_expected_career)

        return _expected_career.lower()

    def normalize_candidate_expected_goals(self):
        _expected_goals = self.candidate_dict['expected_goals']
        _expected_goals = self.clean_text(_expected_goals)

        return _expected_goals

    def normalize_candidate_birthday(self):
        try:
            # print(self.candidate_dict['birthday'])
            _birthday = self.candidate_dict['birthday']
            _birthday = self.clean_text(_birthday)
            match = re.findall(r'^\d{1,2}/\d{1,2}/\d{2,4}$', _birthday)

            if match:
                try:
                    date_time_splited = match[0].split('/')
                    ret_date = datetime.date(
                        int(date_time_splited[-1]),
                        int(date_time_splited[-2]),
                        int(date_time_splited[-3])
                    )
                    return ret_date.strftime('%d-%b-%Y')
                except:
                    return None
            return None
        except:
            return None

    def normalize_candidate_marital_status(self):
        _marital_status = self.candidate_dict['marital_status']
        _marital_status = self.clean_text(_marital_status)

        return _marital_status

    def normalize_candidate_career(self):
        _career = self.candidate_dict['career']
        _career = self.clean_text(_career)

        return _career

    def run_normalize(self, candidate_dict):
        try:
            self.candidate_dict = candidate_dict
            ret_dict = {'url': candidate_dict['url']} if 'url' in candidate_dict else {'url': ''}

            for _field in self.list_field:
                if _field not in self.candidate_dict:
                    ret_dict[_field] = ''
                elif 'normalize_candidate_' + _field in self.normalizable:
                    ret_dict[_field] = self.normalizable['normalize_candidate_' + _field]()
                else:
                    ret_dict[_field] = self.candidate_dict[_field]

            ret_dict['currency_unit'] = ret_dict['expected_salary']['currency_unit']
            ret_dict['salary_normalized'] = ret_dict['expected_salary']['salary_normalized']
            ret_dict['expected_salary_raw'] = candidate_dict['expected_salary']
            if ret_dict['currency_unit'] != -1:
                ret_dict['expected_salary'] = list(map(
                    lambda x: (
                        x * self.exchange_rate[
                            ret_dict['currency_unit']
                        ] if (x * self.exchange_rate[ret_dict['currency_unit']]) > 0 else -1
                    ), ret_dict['salary_normalized']
                ))
            else:
                ret_dict['salary_value'] = [-1]
            return ret_dict
        except Exception as ex:
            try:
                _, _, lineno = sys.exc_info()
                logger.error('Line error: {} - Error: {}'.format(lineno.tb_lineno, ex))
                print(candidate_dict)
            except:
                logger.error('Cannot get line error - Error{}'.format(ex))
            raise ex


class BdsNormalizer:
    def __init__(self, redis_connection):
        self.bds_dict = dict()
        self.list_field = list(set([
            i
            for domain in json.loads(redis_connection.get('bds_rules')).values()
            for i in domain
        ]))

    def run_normalize(self, bds_dict):
        self.bds_dict = bds_dict

        return self.bds_dict
