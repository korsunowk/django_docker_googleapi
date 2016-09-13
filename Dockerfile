FROM python:3.4
ENV PYTHONUNBUFFERED 1
RUN mkdir /project
WORKDIR /project
ADD requirements.txt /project/
RUN pip3 install -r requirements.txt
ADD . /project/