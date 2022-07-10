# Python 3.10
FROM python:3.10
# base folder
WORKDIR /app
# required packages
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
# load web app code
COPY ./templates /app/templates
COPY ./static /app/static
COPY ./main.py /app/main.py
# web app db
COPY ./crf_donors.db /app/crf_donors.db
# run web app
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "80"]