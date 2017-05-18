FROM  docker.io/vanyadndz/scrapy 
ENV PATH /usr/local/bin:$PATH
ENV PATH /home:$PATH
ADD . /home
WORKDIR /home
RUN pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
COPY spiders.py /usr/local/lib/python3.5/site-packages/scrapy_redis
