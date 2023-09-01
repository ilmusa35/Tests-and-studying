"""
In this project I will create programm, which will help me to monitoring job vacancies,
relevated for me.
For scraping, I will use reed.co.uk
"""
import numpy as np
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from datetime import datetime, timedelta
import sqlalchemy as sql
import key
from geopy.geocoders import Nominatim

list_of_requests = ['AI Architect', 'AI Developer', 'AI Engineer', 'AI Programmer', 'AI Research Engineer', 'AI Scientist',
                    'Analytics Engineer', 'BI Analyst', 'BI Developer', 'Business Intelligence', 'Computer Vision', 'Data Analyst',
                    'Data Analytics', 'Data Architect', 'Data DevOps Engineer', 'Data Engineer', 'Data Infrastructure',
                    'Data Integration', 'Data Management', 'Data Manager', 'Data Modeler', 'Data Operations', 'Data Quality',
                    'Data Science', 'Data Scientist', 'Data Specialist', 'Data Strategist', 'Data Visualization',
                    'Deep Learning', 'ETL Developer', 'ETL Engineer', 'Insight Analyst', 'Machine Learning', 'ML Engineer',
                    'MLOps Engineer', 'NLP Engineer', 'Power BI Developer', 'Research Analyst', 'Research Engineer',
                    'Research Scientist', 'Python Developer', 'Python Engineer']

global_skills_list = ['SQL', 'Python', 'Tensorflow', 'Tableau', 'Power BI', 'Scikit', 'Machine Learning', 'Azure', 'API', 'AWS',
                      'PyTorch', 'Django', 'Flask', 'Linux']


def connect_to_sqlalchemy():
    engine = sql.create_engine(f'mysql+mysqlconnector://root:{key.mysqlroot}@127.0.0.1:3306/reed_jobs', echo=False)
    return engine


def create_job_table(name, connect):
    meta = sql.MetaData()

    job_table = sql.Table(
        name, meta,
        sql.Column('job_id', sql.BIGINT, primary_key=True),
        sql.Column('title', sql.Text),
        sql.Column('posted', sql.DateTime),
        sql.Column('company', sql.Text),
        sql.Column('salary_from', sql.Float),
        sql.Column('salary_to', sql.Float),
        sql.Column('location', sql.Text),
        sql.Column('country', sql.Text),
        sql.Column('type', sql.Text),
        sql.Column('link', sql.Text),
        sql.Column('experience', sql.Text),
        sql.Column('skills', sql.Text),
        sql.Column('level', sql.Text),
    )
    meta.create_all(connect)
    return job_table


def remove_duplicates(df_for_check, df_source):

    if len(df_for_check) > 0 and len(df_source) > 0:
        values_to_drop = df_source['job_id'].values
        df_for_check['job_id'] = df_for_check['job_id'].astype(int)
        df_for_check['new'] = ~df_for_check['job_id'].isin(values_to_drop)
        df_for_check = df_for_check[df_for_check['new'] == True]
        # df_for_check.drop(labels=['new'], axis=1, inplace=True)
        df_for_check = df_for_check.drop(labels=['new'], axis=1)
    return df_for_check


def get_urls(request, location=""):
    base_url = "https://www.reed.co.uk/jobs/"
    request_for_url = request.replace(" ", "-")
    if location == "":
        final_url = f'{base_url}{request_for_url}-job'
    else:
        location_for_url = location.replace(" ", "-")
        final_url = f'{base_url}{request_for_url}-job-in-{location_for_url}'

    return final_url


def get_vacation_date(date_txt):
    current_date = datetime.now()

    by_position = date_txt.find("by")
    date_only = date_txt[:by_position]
    date_only = date_only.strip()
    there_is_ago = date_only.find("ago")
    if there_is_ago > 0:
        hours = date_only.find("hour")
        if hours > 0:
            date_in_datetime = datetime.now().strftime("%d.%m.%Y")
        else:
            days = date_only.find("day")
            if days > 0:
                days_ago = int(date_txt.split(' ')[0])
            else:
                weeks = date_only.find("week")
                if weeks > 0:
                    weeks_ago = int(date_txt.split(' ')[0])
                    days_ago = weeks_ago*7
                else:
                    months = date_only.find("month")
                    if months > 0:
                        months_ago = int(date_txt.split(' ')[0])
                        days_ago = months_ago * 30
                    else:
                        # not recognazed... we will use yesterday date in this case
                        days_ago = 1
            date_in_datetime = (current_date - timedelta(days=days_ago)).strftime("%d.%m.%Y")

    else:
        yesterday = date_only.find('Yesterday')
        if yesterday >= 0:
            date_in_datetime = (current_date - timedelta(days=1)).strftime("%d.%m.%Y")
        else:
            date_only = date_only.replace("Feburary", "February")  # error on the website
            date_format = "%d %B %Y"
            year = datetime.now().year
            date_in_datetime = datetime.strptime(f"{date_only} {year}", date_format).strftime("%d.%m.%Y")

    date_res = datetime.strptime(date_in_datetime, "%d.%m.%Y").date()

    return date_res


def fetch_level(df):

    df['level'] = ''
    mask_jun = df['title'].str.contains('Junior', case=False)
    df.loc[mask_jun, 'level'] = 'Junior'
    mask_tr = df['title'].str.contains('Trainee', case=False)
    df.loc[mask_tr, 'level'] = 'Junior'
    mask_gr = df['title'].str.contains('Graduate', case=False)
    df.loc[mask_gr, 'level'] = 'Junior'
    mask_mid = df['title'].str.contains('Middle', case=False)
    df.loc[mask_mid, 'level'] = 'Middle'
    mask_mid = df['title'].str.contains('Mid Level', case=False)
    df.loc[mask_mid, 'level'] = 'Middle'
    mask_sen = df['title'].str.contains('Senior', case=False)
    df.loc[mask_sen, 'level'] = 'Senior'
    mask_sen = df['title'].str.contains('Advanced', case=False)
    df.loc[mask_sen, 'level'] = 'Senior'
    mask_man = df['title'].str.contains('Manager', case=False)
    df.loc[mask_man, 'level'] = 'Manager'
    mask_lead = df['title'].str.contains('Lead', case=False)
    df.loc[mask_lead, 'level'] = 'Lead/Head'
    mask_head = df['title'].str.contains('Head', case=False)
    df.loc[mask_head, 'level'] = 'Lead/Head'
    mask_dir = df['title'].str.contains('Director', case=False)
    df.loc[mask_dir, 'level'] = 'Lead/Head'
    mask_dir = df['title'].str.contains('Principal', case=False)
    df.loc[mask_dir, 'level'] = 'Lead/Head'

    return df


def get_skills(descr_text):

    skills = ""
    for next_skill in global_skills_list:
        find_skill = descr_text.find(next_skill)
        if find_skill >= 0:
            if len(skills) > 0:
                skills = f'{skills}, {next_skill}'
            else:
                skills = next_skill

    return skills


def convert_salary(salary_txt):
    salary_txt = salary_txt.replace(',', '')
    matches = re.findall(r'\b\d+\b', salary_txt)

    if len(matches) >= 2:
        salary_from = int(matches[0])
        salary_to = int(matches[1])
    elif len(matches) == 1:
        salary_from = int(matches[0])
        salary_to = int(matches[0])
    else:
        salary_from = 0
        salary_to = 0

    per_day = salary_txt.find('per day')
    if per_day > 0:
        salary_from = salary_from * 260
        salary_to = salary_to * 260

    if salary_from > salary_to:
        salary_to = salary_from

    return salary_from, salary_to


def compare_exp_level(df):

    df['level'] = np.where((df['level'] == "") & (df['experience'] >= 5), 'Senior', df['level'])
    df['level'] = np.where((df['level'] == "") & (df['experience'] >= 3), 'Middle', df['level'])
    df['experience'] = np.where((df['level'] == "Senior") & (df['experience'].isnull()), 5, df['experience'])
    df['experience'] = np.where((df['level'] == "Middle") & (df['experience'].isnull()), 3, df['experience'])
    return df


def scraping(url):

    start_page = requests.get(url)
    main_page = BeautifulSoup(start_page.text, 'html.parser')
    all_jobs = main_page.find('header', attrs={"class": 'pagination_pagination__heading__hlCzI pagination_pageNumbers__L_ry7 card-header'})
    all_jobs_text = all_jobs.get_text()
    matches = re.search(r'(\d+) jobs', all_jobs_text)
    if matches:
        number_of_jobs = int(matches.group(1))
    else:
        number_of_jobs = 0
    pages = int(number_of_jobs/25 + 1)
    df = pd.DataFrame()
    for page in range(1, pages+1):
        url_page = f'{url}?pageno={page}'
        curr_page = requests.get(url_page)
        main_page_html = BeautifulSoup(curr_page.text, 'html.parser')

        jobs_on_page = main_page_html.findAll('article', attrs={"class": 'card job-card_jobCard__MkcJD'})
        # jobs_on_page = main_page_html.findAll('div', attrs={"class": 'job-card_jobCard__body__86jgk card-body'})
        for job in jobs_on_page:
            job_id = job['data-id']
            job_id = int(job_id.replace("job", ""))
            job_title_el = job.find('h2', class_='job-card_jobResultHeading__title__IQ8iT')
            job_title = job_title_el.get_text()
            posted_el = job.find('div', class_='job-card_jobResultHeading__postedBy__sK_25')
            posted_date = posted_el.get_text()
            posted_date = get_vacation_date(posted_date)
            company = posted_el.find("a").get_text()
            price_location = job.find('ul', class_='job-card_jobMetadata__gjkG3 list-group list-group-horizontal').find_all('li')
            salary = city = job_type = ""
            for i in range(len(price_location)):
                if i == 0:
                    salary = price_location[i].get_text()
                elif i == 1:
                    city = price_location[i].get_text()
                else:
                    job_type = price_location[i].get_text()
            country = 'United Kingdom'  # by default
            try:
                geolocator = Nominatim(user_agent="city_country_app")
                country_location = geolocator.geocode(city, exactly_one=True)
                if country_location:
                    country = country_location.address.split(",")[-1].strip()
            except:
                pass
            salary_from, salary_to = convert_salary(salary)
            link_to_vacancy = job.find('a').get('href')
            full_link = f'https://www.reed.co.uk{link_to_vacancy}'
            vacancy_page = requests.get(full_link)
            vacancy_page_html = BeautifulSoup(vacancy_page.text, 'html.parser')
            descr = vacancy_page_html.find('div', class_="description")
            if descr is None:
                descr = vacancy_page_html.find('div', class_="branded-job--description-container")
            descr_text = descr.get_text()
            # skills_on_page = vacancy_page_html.find('div', class_="skills")
            # if skills_on_page is None:
            skills = get_skills(descr_text)
            # else:
            #     list_of_skills = skills_on_page.findAll('li', class_='lozenge skill-name')
            #     skills = ""
            #     for next_skill in list_of_skills:
            #         this_skill = next_skill.get_text()
            #         if len(skills) > 0:
            #             skills = f'{skills}, {this_skill}'
            #         else:
            #             skills = this_skill
            #         need_to_global = global_skills_list.find(this_skill)
            #         if need_to_global < 0:
            #             global_skills_list.append(this_skill)

            exp_matches = re.search(r'(\d+) years', descr_text)
            experience = None
            if exp_matches:
                experience = int(exp_matches.group(1))
                if experience > 7:
                    experience = 0

            new_row = pd.DataFrame([{
                "job_id": job_id,
                "title": job_title,
                "posted": posted_date,
                "company": company,
                "salary_from": salary_from,
                "salary_to": salary_to,
                "location": city,
                "country": country,
                "type": job_type,
                "link": full_link,
                "experience": experience,
                "skills": skills,
            }])
            df = pd.concat([df, new_row], ignore_index=True)

    df = fetch_level(df)
    df = compare_exp_level(df)

    return df


def save_to_sql(df):
    connection = connect_to_sqlalchemy()
    jobs_sql = create_job_table("jobs", connection)
    query = jobs_sql.select()
    with connection.connect() as conn:
        jobs_sql_df = pd.read_sql(sql=query, con=conn)
        df = remove_duplicates(df, jobs_sql_df)
        df.to_sql(name='jobs', con=conn, if_exists='append', index=False)


def main():
    df = pd.DataFrame()
    # for request in list_of_requests:
    for index in range(len(list_of_requests)):  # 0,2
        print(f'Scanning {index} of {len(list_of_requests)} - {list_of_requests[index]}')
        url = get_urls(list_of_requests[index], "")
        next_df = scraping(url)
        df = pd.concat([df, next_df], ignore_index=True)
        df.drop_duplicates(subset=['job_id'], keep="last", inplace=True)
        save_to_sql(next_df)

    df.to_csv("all_data_scientists_vacancies.csv")
    print('All data scraped and uploaded to the SQL')


main()
