import re
import datetime
import psycopg2


def clean_text(_text):
    if _text is None:
        return ''
    _text = re.sub(r'\n+', '\n', _text)
    _text = re.sub(r'\s+', ' ', _text)
    return _text.strip()


def normalize_salary(salary):
    try:
        if salary is None:
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
            salary = re.sub(r"[^0-9.,]+", '', salary)
            return int(salary.strip()) * 1000000, 'VND'

        if int(salary) > 100000:
            return int(salary), 'VND'

        return int(salary) * 23000, 'USD'

    except Exception as ex:
        print('Normalize salary ERROR - {}'.format(str(ex)))
        raise Exception('Invalid Salary, This record might not be job. Del this job\n')


def normalize_info(info):
    info = clean_text(info)

    return info


def normalize_deadline_submit(deadline_submit):
    try:
        deadline_submit = clean_text(deadline_submit)

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
            return lastest_date.strftime("%b-%d-%Y")
        return deadline_submit

    except Exception as ex:
        print('Normalize deadline_submit ERROR - {}'.format(str(ex)))
        return ''


def normalize_experience(experience):
    experience = clean_text(experience)
    if ':' in experience:
        experience = experience.split(':')[-1].strip()

    if experience == '':
        experience = None

    return experience


def normalize_title(title):
    title = clean_text(title)

    return title


def normalize_company(company):
    company = clean_text(company)

    return company


def normalize_location(location):
    location = clean_text(location)
    if ':' in location:
        location = location.split(':')[-1].strip()

    return location


def normalize_degree_requirements(degree_requirements):
    degree_requirements = clean_text(degree_requirements)
    if ':' in degree_requirements:
        degree_requirements = degree_requirements.split(':')[-1].strip()

    if degree_requirements == '':
        degree_requirements = None

    return degree_requirements


def normalize_no_of_opening(no_of_opening):
    try:
        no_of_opening = clean_text(no_of_opening)
        if no_of_opening == '':
            return -1

        if ':' in no_of_opening:
            no_of_opening = no_of_opening.split(':')[-1].strip()

        no_of_opening = int(no_of_opening)

        return no_of_opening
    except:
        return -1


def normalize_formality(formality):
    formality = clean_text(formality)

    if ':' in formality:
        formality = formality.split(':')[-1].strip()

    return formality


def normalize_position(position):
    position = clean_text(position)
    if ':' in position:
        position = position.split(':')[-1].strip()

    return position


def normalize_gender_requirements(gender_requirements):
    gender_requirements = clean_text(gender_requirements)

    if ':' in gender_requirements:
        gender_requirements = gender_requirements.split(':')[-1].strip()

    if gender_requirements == '':
        gender_requirements = None

    return gender_requirements


def normalize_career(career):
    career = clean_text(career)
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


def normalize_description(description):
    description = clean_text(description)

    if description == '':
        description = None

    return description


def normalize_benefit(benefit):
    benefit = clean_text(benefit)

    if benefit == '':
        benefit = None

    return benefit


def normalize_job_requirements(job_requirements):
    job_requirements = clean_text(job_requirements)

    if job_requirements == '':
        job_requirements = None

    return job_requirements


def normalize_profile_requirements(profile_requirements):
    profile_requirements = clean_text(profile_requirements)

    if profile_requirements == '':
        profile_requirements = None

    return profile_requirements


def normalize_contact(contact):
    contact = clean_text(contact)

    if contact == '':
        contact = None

    return contact


def normalize_other_info(other_info):
    other_info = clean_text(other_info)

    if other_info == '':
        other_info = None

    return other_info


def normalize_job_crawler(job_dict):
    n_salary, currency_unit = normalize_salary(job_dict['salary'])
    return {
        'title': job_dict['title'],
        'salary_normalize': n_salary,
        'currency_unit': currency_unit,
        'salary': normalize_title(job_dict['title']),
        'url': job_dict['url'],
        'company': normalize_company(job_dict['company']),
        'location': normalize_location(job_dict['location']),
        'info': normalize_info(job_dict['info']),
        'degree_requirements': normalize_degree_requirements(job_dict['degree_requirements']),
        'deadline_submit': normalize_deadline_submit(job_dict['deadline_submit']),
        'experience': normalize_experience(job_dict['experience']),
        'no_of_opening': normalize_no_of_opening(job_dict['no_of_opening']),
        'formality': normalize_formality(job_dict['formality']),
        'position': normalize_position(job_dict['position']),
        'gender_requirements': normalize_gender_requirements(job_dict['gender_requirements']),
        'career': normalize_career(job_dict['career']),
        'description': normalize_description(job_dict['description']),
        'benefit': normalize_benefit(job_dict['benefit']),
        'job_requirements': normalize_job_requirements(job_dict['job_requirements']),
        'profile_requirements': normalize_profile_requirements(job_dict['profile_requirements']),
        'contact': normalize_contact(job_dict['contact']),
        'other_info': normalize_other_info(job_dict['other_info']),
    }


def normalize_job(job_dict):
    n_salary, currency_unit = normalize_salary(job_dict['salary'])
    return {
        'id': job_dict['id'],
        'crawl_date': str(job_dict['crawl_date']),
        'title': job_dict['title'],
        'salary_normalize': n_salary,
        'currency_unit': currency_unit,
        'salary': normalize_title(job_dict['title']),
        'url': job_dict['url'],
        'company': normalize_company(job_dict['company']),
        'location': normalize_location(job_dict['location']),
        'info': normalize_info(job_dict['info']),
        'degree_requirements': normalize_degree_requirements(job_dict['degree_requirements']),
        'deadline_submit': normalize_deadline_submit(job_dict['deadline_submit']),
        'experience': normalize_experience(job_dict['experience']),
        'no_of_opening': normalize_no_of_opening(job_dict['no_of_opening']),
        'formality': normalize_formality(job_dict['formality']),
        'position': normalize_position(job_dict['position']),
        'gender_requirements': normalize_gender_requirements(job_dict['gender_requirements']),
        'career': normalize_career(job_dict['career']),
        'description': normalize_description(job_dict['description']),
        'benefit': normalize_benefit(job_dict['benefit']),
        'job_requirements': normalize_job_requirements(job_dict['job_requirements']),
        'profile_requirements': normalize_profile_requirements(job_dict['profile_requirements']),
        'contact': normalize_contact(job_dict['contact']),
        'other_info': normalize_other_info(job_dict['other_info']),
    }
