FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV SUMO_HOME=/usr/share/sumo
ENV PATH="${SUMO_HOME}/bin:${PATH}"

RUN sed -i 's|http://archive.ubuntu.com|http://mirrors.wikimedia.org|g' /etc/apt/sources.list && \
    sed -i 's|http://security.ubuntu.com|http://mirrors.wikimedia.org|g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sumo \
    sumo-tools \
    sumo-doc \
    xorg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["/bin/bash"]