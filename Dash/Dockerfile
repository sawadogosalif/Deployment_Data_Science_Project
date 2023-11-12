FROM python:3.9
COPY . /usr/app/
WORKDIR /usr/app/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 7000
ENTRYPOINT ["gunicorn", "main:application", "-b", "0.0.0.0:7860", "--workers=1"]

