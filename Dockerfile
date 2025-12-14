FROM python:3.12

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources

RUN apt update && apt install -y libgl1 libglx-mesa0

RUN pip install -r requirements.txt

WORKDIR /m7a

CMD ["python", "main.py"]