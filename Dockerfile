FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ["uwsgi.ini", "*.py", "/app/"]
COPY ["./static/", "/app/static/"]
COPY ["./templates/", "/app/templates/"]
COPY ["./res/", "/app/res/"]

#ENTRYPOINT "/bin/bash"
