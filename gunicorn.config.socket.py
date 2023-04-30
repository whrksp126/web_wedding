# File name: gunicorn.config.socket.py

import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1

# Nginx server 블록에서 설정한 내부 소켓 경로 사용
bind = 'unix:/tmp/app.sock'

# wsgi_app 지정
# 명령어로 입력했던 'app:create_app()' 을 설정 파일에서 지정
wsgi_app = 'app:create_app()'

errorlog = './gunicorn_log/errorlog.txt'
accesslog = './gunicorn_log/accesslog.txt'