# 
FROM python:3.11
# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --upgrade pip
RUN pip install --no-cache-dir  requests matrix-nio boto3 fastapi gunicorn uvicorn prisma pillow

# 
COPY . /code

ENV PORT=80

RUN prisma generate
# 
CMD exec gunicorn --bind :$PORT --workers 2 --timeout 0  --worker-class uvicorn.workers.UvicornWorker --log-level debug --threads 8 main:app
