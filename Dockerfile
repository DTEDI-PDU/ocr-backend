FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 4000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
