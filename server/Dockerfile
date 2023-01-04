FROM python:3.10.9

WORKDIR /logistics-station

RUN pip install pymongo python-dotenv

COPY . .

CMD [ "python","main.py" ]