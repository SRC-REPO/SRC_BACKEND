FROM python:3.8

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt


# COPY . /code/

# CMD ["gunicorn", "main:app", "--workers","4","--worker-class","uvicorn.workers.UvicornWorker","--bind", "0.0.0.0:8432"]
