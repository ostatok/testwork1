#! /usr/bin/env python
# -*- coding: utf-8 -*-

#
# Run this program in a way like a daemon, restart after reboot:
# nohup python2.7 main.py &
#

import requests
import datetime
import smtplib
import configparser
import schedule
import time
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', -1)

# vars
config = configparser.ConfigParser()
config.read('config.ini')

mail_server = config['MAIL']['server']
mail_server_port = config['MAIL']['port']
mail_server_user = config['MAIL']['user']
mail_server_password = config['MAIL']['password']
sending_time = config['MAIL']['sending_time']

confluence_connection_string = config['CONFLUENCE']['confluence_connection_string']
confluence_user = config['CONFLUENCE']['user']
confluence_password = config['CONFLUENCE']['pass']


def get_dataframe():
    r = requests.get(confluence_connection_string,
                     auth=(confluence_user, confluence_password))
    df_list = pd.read_html(r.content, header=0, encoding='UTF-8')
    return df_list[0]


def today_celebration(birthday):
    # Add to the date current year and find the difference.
    now = datetime.datetime.now()
    year = now.strftime("%Y")
    bd = str(birthday) + "." + year
    dr = datetime.datetime.strptime(bd, "%d.%m.%Y")
    now_str = now.strftime("%d.%m.%Y")
    now_date = datetime.datetime.strptime(now_str, "%d.%m.%Y")
    t1 = dr - now_date
    print t1.days
    if t1.days >= -7 and t1.days <= 1:
        return 1, str(birthday)


def send_email(msg, target):
    print msg
    print target
    server = smtplib.SMTP(mail_server, mail_server_port)
    server.login(mail_server_user, mail_server_password)
    server.sendmail("python@mail", target, msg)


def main():
    """
    Program send birthday reminder by e-mail to every person of team except birthday boy/girl.
    Information about people it takes from Confluence server.
    It should be run this way to be like a daemon:
            nohup python2.7 main.py &
    It sends e-mails at time, defined in config.ini every work day.
    Configuration parameters it also keeps in config.ini
    :args: config.ini
    """
    df = get_dataframe()
#   print(df)
    for i in df[u"№"]:
        try:
            print i
            hb, dr = today_celebration(df[u"День рождения"][i])
            if hb == 1:
                for j in (df[u"№"]):
                    if df[u'Комната'][j] != u'уволен':
                        if j == i:
                            pass
                        else:
                            message = (df[u"ФИ"][i] + u' празднует день рождения ' + dr)
                            target = df[u"e-mail"][j]
                            send_email(message, target)
        #except Exception as e: print(e)
        except:
            pass


if __name__ == "__main__":
    #Schedule to start daily at exact time
    schedule.every(1).to(5).days.at(sending_time).do(main())
    while True:
        schedule.run_pending()
        time.sleep(3600)
#       main()