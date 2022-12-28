FROM python:3.10.9

WORKDIR /logistics-node

RUN pip install pymongo python-dotenv

COPY ./ /logistics-node

CMD [ "python","main.py" ]