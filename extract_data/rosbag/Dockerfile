# For more information, please refer to https://aka.ms/vscode-docker-python
FROM ros:noetic-ros-core

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install apt requirements
RUN apt-get update --fix-missing && apt-get install -y python3 python3-pip
RUN apt-get install -y libopencv-dev=4.2.0+dfsg-5 libopencv-contrib-dev
RUN apt-get install -y ros-noetic-cv-bridge ros-noetic-grid-map-msgs
RUN apt-get install -y ffmpeg

# Install pip requirements
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# cleanup apt dir
RUN rm -rf /var/lib/apt/lists/*

# Copy over files
WORKDIR /app
COPY scripts/ /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden (cmd vs. entrypoint)
# For more information, please refer to https://aka.ms/vscode-docker-python-debug
COPY entrypoint.sh .
CMD ["./entrypoint.sh"]
