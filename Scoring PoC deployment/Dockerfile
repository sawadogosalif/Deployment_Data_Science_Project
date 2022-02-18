FROM continuumio/miniconda3
COPY . /usr/app/
EXPOSE 5000
WORKDIR /usr/app/
RUN pip install -r requirements.txt
CMD python 03_streamlit_scoring_prediction.py