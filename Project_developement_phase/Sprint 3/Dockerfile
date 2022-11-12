FROM python:3.10.8-bullseye

WORKDIR /app

COPY . /app

RUN apt update
RUN apt upgrade
RUN apt install -y gcc python3-dev 
RUN pip install --upgrade pip setuptools wheel
RUN pip install cryptography

RUN pip3 install -r requirements.txt

## ibm_db install prob

ENV FLASK_APP=run.py

ENTRYPOINT ["python"]
CMD ["manager.py"]