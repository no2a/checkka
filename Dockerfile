FROM python:3.12-slim
RUN pip install psutil
ADD ./http_server.py /
