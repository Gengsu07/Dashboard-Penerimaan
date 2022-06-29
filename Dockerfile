FROM python:3.8

WORKDIR /APPS

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /APPS

EXPOSE 8501
ENTRYPOINT [ "streamlit","run" ]

CMD ["andteam.py"]