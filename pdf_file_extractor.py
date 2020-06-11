from bs4 import BeautifulSoup
import requests
import tabula
from datetime import datetime
import pandas as pd
import csv
import os

def day_end_time(list_pdfs):
    time_stamps = [i.split('_')[2] for i in list_pdfs] 
    pm = {}
    am = {}
    for index,i in enumerate(time_stamps):
        if 'PM' in i:
            pm[index] = int(i.replace('PM','')[:2])
            break
        else:
            am[index] = int(i.replace('AM','')[:2])
    if am == {} and pm != {}:
        result_time = max(pm.values())
        key = [key  for (key, value) in pm.items() if value == result_time]
    if pm == {} and am !={}:
        result_time = max(am.values())
        key = [key  for (key, value) in am.items() if value == result_time]
    if am != {} and pm != {}:
        result_time = max(pm.values())
        key = [key  for (key, value) in pm.items() if value == result_time]
    return list_pdfs[key[0]]

def data_extractor_ap():
    base_url = 'http://hmfw.ap.gov.in/'
    url = 'http://hmfw.ap.gov.in/covid_19_dailybulletins.aspx'
    page = requests.get(url)
    soup = BeautifulSoup(page.content,'html.parser')
    dates = soup.findAll('div',class_="col-md-2")
    date_url_dict = {}
    for element in soup.findAll('div',class_="col-md-2"):
        data_url = base_url + element.find('a')['href']
        date_str = element.find('a').get_text()
        date = datetime.strptime(date_str, '%d-%m-%Y').date()
        with open('updated_date.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
        cutoff_date = datetime(2020, 4, 14).date()
        if date >= cutoff_date:
            detailed_page = requests.get(data_url)
            soup_pdf = BeautifulSoup(detailed_page.content,'html.parser')
            list_pdf_urls = []
            for ele in soup_pdf.findAll('a'):
                try :
                    if '.pdf' in ele['href'] :
                        list_pdf_urls.append(base_url+ele['href'])
                except:
                    pass
            if [ pdf_url for pdf_url in list_pdf_urls if 'AM' in pdf_url or 'PM' in pdf_url]:
                pdf_url = day_end_time(list_pdf_urls)
                date_url_dict[date] = pdf_url
            else:
                if list_pdf_urls != []:
                    pdf_url = list_pdf_urls[0]
                    date_url_dict[date] = pdf_url
                else:
                    pdf_url = 'no_informartion'
                    date_url_dict[date] = pdf_url
    return date_url_dict
       
dist_rows = ['Ananthapur','Chittoor','East Godavari','Guntur','Kadapa','Krishna','Kurnool','Nellore','Prakasam','Srikakulam','Vishakapatnam','Vizianagaram','West Godavari','Total']
df_active = pd.DataFrame()
df_active['District'] = dist_rows
df_discharged = pd.DataFrame()
df_discharged['District'] = dist_rows
df_deaths = pd.DataFrame()
df_deaths['District'] = dist_rows
df_total = pd.DataFrame()
df_total['District'] = dist_rows

current_dir = os.path.dirname(os.path.abspath(__file__))
if 
# if date_url_dict == {}:
date_url_dict = data_extractor_ap()

for (key, value) in date_url_dict.items():
    if value != 'no_informartion':
        df = tabula.read_pdf(value, pages='all')
        df = df[0]
        if 'Unnamed: 0' in df.columns:
            df = df.T.set_index(0).T
            df = df.reset_index()
        if 'Deceased' in df.columns:
            df.rename(columns = {'Deceased' : 'Deaths'},inplace=True)
        if 'Active' in df.columns:
            df.rename(columns = {'Active' : 'Active Cases'},inplace=True)
        df = df.sort_values(["District"], ascending = True)
        df_active[str(value)] = df['Active Cases']
        df_deaths[key] = df['Deaths']
        df_discharged[key] = df['Discharged']
        df_total[key] = df['Total']


print(df_active)
# # transpose rows for data visuvalization
# df_active = df_active.T
# df_active.to_csv(r'E:\Covid19_ap_analysis\active.csv')
# df_deaths = df_deaths.T
# df_deaths.to_csv('E:\Covid19_ap_analysis\deaths.csv')
# df_discharged = df_discharged.T
# df_discharged.to_csv('E:\Covid19_ap_analysis\discharged.csv')
# df_total = df_total.T
# df_total.to_csv(r'E:\Covid19_ap_analysis\total.csv')



