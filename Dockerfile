FROM ubuntu:latest

# Set shell
SHELL ["/bin/bash", "-c"]

# Update & Upgrade | Install Python, Pip and Virtualenv
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y python3-pip python-dev build-essential python3-venv

# Create venv and activate it
RUN python3 -m venv venv && \
    source venv/bin/activate

# Show logs in real time
ENV PYTHONUNBUFFERED 1

# Copy files from local to Docker host
COPY . ./library-api/

# Set root dir
ENV APP_HOME ./library-api

# Isntall requirements
RUN pip install -r $APP_HOME/requirements.txt