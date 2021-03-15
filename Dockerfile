FROM python:3.8
COPY . /opt
ENV NSC_PORT=80
WORKDIR /opt
RUN pip install -r requirements.txt
EXPOSE 80
CMD [ "python", "-u", "./pf.py" ]
