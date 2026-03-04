FROM jenkins/jenkins:2.452.1-lts-jdk17

USER root

# Install Python 3 + pip + Robot Framework dependencies + curl + git
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        curl \
        git \
        openssh-client \
        android-tools-adb \
    && rm -rf /var/lib/apt/lists/*

# Install Robot Framework and required libraries globally
RUN pip3 install --no-cache-dir --break-system-packages \
        robotframework==6.1.1 \
        robotframework-sshlibrary==3.8.0 \
        robotframework-requests==0.9.6 \
        robotframework-jsonlibrary==0.5 \
        paramiko==3.4.0 \
        httpx==0.27.0

USER jenkins

# Copy the plugin list and install plugins
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Copy JCasC configuration
COPY casc/ /var/jenkins_home/casc_configs/

ENV CASC_JENKINS_CONFIG=/var/jenkins_home/casc_configs
