FROM python:3.8
COPY . /opt
WORKDIR /opt
RUN pip install -r requirements.txt
EXPOSE 80
CMD [ "python", "-u", "./pf.py" ]
