# FROM --platform=windows/amd64 python:3.10.6-windowsservercore-ltsc2022

# RUN mkdir "C:\Program` Files\APPS"
# WORKDIR "C:\Program` Files\APPS"


FROM python:latest

RUN mkdir APPS
WORKDIR /APPS
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache
COPY . /APPS


EXPOSE 8501
ENTRYPOINT [ "streamlit","run" ]

CMD ["andteam.py"]