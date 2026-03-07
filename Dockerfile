FROM python:3.12

RUN apt-get update && \
	apt-get install -y inkscape && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -qqq --disable-pip-version-check -r requirements.txt

COPY . .

RUN scripts/init.sh

CMD ["python", "updater.py"]