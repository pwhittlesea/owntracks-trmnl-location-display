FROM python:3.14

# Needed for html2image
RUN apt-get update -y && apt-get install -y chromium

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--proxy-headers", "--forwarded-allow-ips", "*", "--port", "80"]
