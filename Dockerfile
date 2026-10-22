# EOL Python 3.8 on EOL Debian 10 "buster"
FROM python:3.8-buster
WORKDIR /srv
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV AWS_SECRET_ACCESS_KEY=q8Zr3Kx9mT2vLp7WnB4cY6hJ1sDfG5aE0uRiOkPz
EXPOSE 5000
CMD ["python", "-m", "app.main"]
