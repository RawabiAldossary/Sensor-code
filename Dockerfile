FROM python:3.10

RUN apt-get update & apt-get upgrade 

# SET MY WORKING DIR --> LOOK THIS UP 
WORKDIR /sever

#  COPY FROM MY COMPUTER TO THE CONTAINER /server dir
COPY . .

ADD server.py .

# LEARN ABOUT REQUIRMENT FILE
ADD requirments.txt .
ADD auxutils.py       .

RUN pip install  -r requirments.txt
CMD ["python" ,"./server.py"]