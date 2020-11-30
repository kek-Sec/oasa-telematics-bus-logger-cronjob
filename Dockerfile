FROM python:3

ADD . /

RUN pip install aiohttp
RUN pip install requests
RUN pip install schedule

CMD [ "python", "./oasa.py" ]
