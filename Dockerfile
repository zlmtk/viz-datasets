FROM ubuntu:20.04
RUN apt-get update 
RUN apt install -y  python3  python3-pip
RUN pip install dash 
RUN pip install dash-bootstrap-components 
RUN pip install Pillow
RUN pip install pandas 
RUN pip install matplotlib 

RUN mkdir /apps
WORKDIR /apps

ADD  assets /apps/assets 
ADD  scatter-dash.py /apps  

RUN cd /apps 
ENTRYPOINT ["python3.8", "scatter-dash.py"]   
