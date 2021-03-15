FROM python:3.8
COPY . /opt
WORKDIR /opt
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org twisted
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org flask
CMD [ "python", "-u", "./app.py" ]
