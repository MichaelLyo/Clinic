#!/usr/bin/env bash

#sed -ig 's/DEBUG = True/DEBUG = False/'  ./LoanCredit/settings.py
#rm ./LoanCredit/settings.pyg

scp -r ./Clinic/ ./MyClinic/  ./manage.py ubuntu@118.25.6.157:myproject/clinic
#ssh ubuntu@212.64.32.162 "sudo service nginx restart ; uwsgi --reload /home/ubuntu/LoanCredit/uwsgi/uwsgi.pid"
#ssh ubuntu@118.25.6.157 "python myproject/clinic/manage.py runserver 0.0.0.0:1213 --insecure"
ssh ubuntu@118.25.6.157 "cd myproject/clinic ; ./restart.sh "
#ssh ubuntu@118.25.6.157 "python manage.py runserver 0.0.0.0:1213 --insecure"

#sed -ig 's/DEBUG = False/DEBUG = True/'  ./LoanCredit/settings.py
#rm ./LoanCredit/settings.pyg

#在运行时强制Django处理静态文件：(不需要配置uwsgi和nginx)
#python manage.py runserver 0.0.0.0:88 --insecurena
