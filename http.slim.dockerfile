FROM python:3.6-slim

ENV HOME=/app NAME=nk_unicorn

WORKDIR $HOME

COPY requirements.txt $HOME/

RUN pip3 install --upgrade pip \
    && pip3 install -r requirements.txt 
# pip3 install -e 

COPY . $HOME/

ENV FLASK_APP=$HOME/http-wrapper/app.py
CMD ["flask", "run", "--host=0.0.0.0"]

# CMD ["python3", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "5000"]