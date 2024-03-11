# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

ARG USER_NAME=user
ARG USER_UID=1000
ARG USER_GID=1000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN groupadd ${USER_NAME} --gid ${USER_GID} \
    && useradd -l -m ${USER_NAME} -u ${USER_UID} -g ${USER_GID} -s /bin/bash \
    && usermod -aG sudo ${USER_NAME}

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Enable non-root user
ENV USER=${USER_NAME}
USER ${USER_NAME}

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "ardupilot_bin2csv.py"]
