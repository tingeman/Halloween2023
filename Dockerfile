# For more information, please refer to https://aka.ms/vscode-docker-python
FROM ubuntu:latest

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt update && apt upgrade
RUN apt-get install python3 python3-pip git -yqq
RUN apt-get install -y iproute2 iputils-ping net-tools curl
RUN apt-get install -y nano
#RUN apt-get install python3-requests-oauthlib python3-websocket -yqq
#RUN apt-get install python3-webview python3-selenium python3-geopy

WORKDIR /pychromecast

# Clone a GitHub repository
RUN git clone https://github.com/home-assistant-libs/pychromecast .

# If there's a requirements.txt file:
RUN --mount=type=cache,mode=0755,target=/root/.cache pip3 install -r requirements.txt

# If the repository is set up as a Python package with setup.py:
RUN pip3 install .

WORKDIR /Halloween2023
RUN git clone https://github.com/tingeman/Halloween2023 .

# Install pip requirements
RUN --mount=type=cache,mode=0755,target=/root/.cache pip3 install -r ./app/requirements.txt
#RUN python3 -m pip install -r requirements.txt


# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]
