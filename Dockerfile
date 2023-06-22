FROM python:3.7
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
RUN apt-get install -yqq unzip
# Set display port as an environment variable
ENV DISPLAY=:99
RUN pip install --upgrade pip
WORKDIR /app
RUN mkdir -p REPORT
ADD ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./ /app
ENTRYPOINT ["python", "quora_bn.py", "prod"]
#ENTRYPOINT ["tail","-f","/dev/null"]