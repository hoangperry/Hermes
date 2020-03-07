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

    def normalize(self, job_dict):
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
        self.list_field = list(set([
            i
            for domain in json.loads(redis_connection.get('candidate_rules')).values()
            for i in domain
        ]))

    def normalize(self, candidate_dict):
        self.candidate_dict = candidate_dict
        ret_dict = dict()
        for _field in self.list_field:
            if _field not in self.candidate_dict:
                ret_dict[_field] = ''
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

    def normalize(self, bds_dict):
        self.bds_dict = bds_dict

        return self. bds_dict
