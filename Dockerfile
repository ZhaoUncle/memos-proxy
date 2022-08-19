FROM python:3.6.8-alpine

RUN mkdir /app
COPY memos.py /app 
COPY requirements.txt /app
COPY config_demo.ini /app
RUN pip install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /app

CMD ["python3","/app/memos.py"]