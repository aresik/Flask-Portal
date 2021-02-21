FROM ubuntu:16.04
RUN apt-get update -y
RUN apt-get install -y apt-utils
RUN apt-get install -y python-pip
RUN apt-get install -y python-dev build-essential
RUN apt-get install -y libcurl4-openssl-dev libssl-dev nano python-mysqldb
COPY flask-portal /flask-portal
WORKDIR /flask-portal
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
