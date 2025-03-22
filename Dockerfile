FROM python:3.11

WORKDIR /project_name

COPY requirements.txt /project_name/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /project_name

EXPOSE 8001