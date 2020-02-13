import psycopg2
import json
import glob
import datetime
import os
from crawler.application.common.helpers.normalizer import *

json_out_dir = 'json_out/'


def get_all_data_from_db(pg_host="35.186.148.118",
                         pg_port="5432",
                         pg_user="jobnet",
                         pg_pass="jobnet2020",
                         pg_db="jobnet_db"):

    connection = psycopg2.connect(
        host=pg_host,
        port=pg_port,
        user=pg_user,
        password=pg_pass,
        database=pg_db
    )
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM public.job;")
    jobs = cursor.fetchall()

    all_jobs = list()
    for job in jobs:
        data_job = job[1]
        data_job['id'] = job[0]
        data_job['crawl_date'] = job[-1]
        all_jobs.append(data_job)

    all_jobs = normalize_all_data(all_jobs)

    return all_jobs


def write_dict_to_json(dict_to_write, name_out):
    file_out = open(name_out, mode='w', encoding='utf-8')
    file_out.write(json.dumps(dict_to_write, indent=4, ensure_ascii=False))
    file_out.close()


def normalize_all_data(all_jobs):
    normalized_job = list()

    for job in all_jobs:
        try:
            normalized_job.append(normalize_job(job))
        except Exception as ex:
            print(ex)
            continue

    return normalized_job


def get_nearest_filename():
    list_file_date = list()
    for file_name in glob.glob(json_out_dir + '*.json'):
        date_i = file_name.split('/')[-1].split('.')[0].split('-')
        date_i = datetime.date(int(date_i[-1]), int(date_i[-2]), int(date_i[-3]))
        if date_i == datetime.date.today():
            continue
        list_file_date.append({
            'date': date_i,
            'file_name': file_name
        })
    if list_file_date.__len__() == 0:
        return None

    return max(list_file_date, key=lambda x: x['date'])['file_name']


def non_duplicate_job(today_job, past_job):
    ret_jobs = list()
    for job in today_job:
        duplicate = False
        for job_2 in past_job:
            if job['url'] == job_2['url']:
                print(job['url'])
                duplicate = True
                break
        if not duplicate:
            ret_jobs.append(job)

    print(ret_jobs.__len__())
    return ret_jobs


if __name__ == '__main__':
    nearest_filename = get_nearest_filename()
    today_filename = json_out_dir + datetime.date.today().strftime("%d-%m-%Y") + '.json'

    if nearest_filename is not None:
        nearest_json = json.load(open(nearest_filename, mode='r', encoding='utf-8'))
        write_dict_to_json(non_duplicate_job(get_all_data_from_db(), nearest_json), today_filename)
    else:
        write_dict_to_json(get_all_data_from_db(), today_filename)

    os.system('scp -i ~/.ssh/ggcl {} hoangvm@35.186.148.118:'.format(today_filename))
    # get_all_data_from_db()
