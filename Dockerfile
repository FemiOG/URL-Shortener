FROM tiangolo/uwsgi-nginx-flask:python3.6
RUN mkdir /url-shortener
WORKDIR /url-shortener
RUN cd /url-shortener
ADD . /url-shortener
RUN pip3 install --upgrade setuptools && pip3 install -r requirements.txt
EXPOSE 80
ENV FLASK_APP app.py
ENV FLASK_DEBUG 0
CMD ./run.sh