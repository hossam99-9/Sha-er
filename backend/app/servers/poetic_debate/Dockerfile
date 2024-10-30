FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Update and install necessary system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install required Python packages
COPY backend/app/servers/poetic_debate/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN git clone https://github.com/ARBML/qawafi
RUN pip install -r qawafi/demo_requirements.txt

# Install Bohour library for detrmining qafya
RUN git clone https://github.com/ARBML/Bohour.git
RUN cd Bohour && python3 setup.py install


COPY . /app/

# For evaluation
RUN cd /app/backend/lib/bert_score && pip install .

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV PYTHONPATH "${PYTHONPATH}:/app/backend"