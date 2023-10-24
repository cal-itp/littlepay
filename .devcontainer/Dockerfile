FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USER=calitp

RUN useradd --create-home --shell /bin/bash $USER && \
    mkdir /home/$USER/.littlepay && \
    chown -R $USER /home/$USER

USER $USER
ENV PATH "$PATH:/home/$USER/.local/bin"
WORKDIR /home/$USER/app

RUN python -m pip install --upgrade pip

COPY .git .git
COPY littlepay littlepay
COPY pyproject.toml pyproject.toml
RUN pip install -e .[dev,test]

CMD ["sleep", "infinity"]
