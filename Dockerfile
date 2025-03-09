FROM python:3.12
WORKDIR /parser

# update apt and install python3 and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# install pip packages
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# ENV
ENV TIME_TO_SLEEP=500

COPY . .

CMD ["python", "main.py"]

