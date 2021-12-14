FROM python:2.7-alpine

WORKDIR /app

COPY  . .

RUN pip install -r requirements.txt

CMD ["sh", "./start_app.sh"]

EXPOSE 7111