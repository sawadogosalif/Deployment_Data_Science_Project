FROM python:3.9
COPY . /usr/app/
WORKDIR /usr/app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 7000
ENTRYPOINT ["gunicorn", "main:application", "-b", "0.0.0.0:7860", "--workers=1"]

# https://medium.com/@feventsegay6/synchronous-vs-asynchronous-web-services-4b9764ba85ee
# Gunicorn is an app server that interacts with your web-application using the WSGI protocol. 
# This means that Gunicorn can serve applications written in synchronous web-frameworks such as Flask OR or Django
The role of the Gunicorn master process is to make sure that the number of workers is the same as the ones defined in the settings. 
# So if any of the workers die, the master process starts another one. 
# Gunicorn itself is not compatible with FastAPI because FastAPI uses the fresh ASGI standard.
