FROM python:3.9
ENV CASSANDRA_HOST = ""
WORKDIR /app/
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8080
CMD python3 sentiment.py