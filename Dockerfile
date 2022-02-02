FROM ubuntu:20.04

#########################################
### Python                                                               
RUN apt update && apt -y install git wget build-essential
RUN apt install -y python3 python3-pip
RUN ln -s python3 /usr/bin/python
RUN DEBIAN_FRONTEND=noninteractive apt install -y python3-tk

#########################################
### Numpy
RUN pip install numpy

#########################################
### gfortran
RUN apt update && apt install -y gfortran

#########################################
RUN mkdir /home/root
ENV HOME=/home/root
ENV LD_LIBRARY_PATH=$HOME/lib
RUN mkdir /repos

# lapack, blas
RUN apt update && apt install -y liblapack-dev libopenblas-dev

# python dependencies for hither
RUN pip install click simplejson requests

# FMM3D - 12/17/21
RUN git clone https://github.com/flatironinstitute/FMM3D /repos/FMM3D \
    && cd /repos/FMM3D \
    && git checkout bc852a8de5b1d08acebaec15ecfcc5442c6ceaeb \
    && make install
RUN cd /repos/FMM3D && make python

# fmm3dbie - 12/17/21
RUN git clone https://github.com/fastalgorithms/fmm3dbie.git /repos/fmm3dbie \
    && cd /repos/fmm3dbie \
    && git checkout b4682e513355906943d710900b05671603e648d8 \
    && make install
RUN cd /repos/fmm3dbie && make python

# miniwasp - 12/17/21
RUN git clone https://github.com/mrachh/miniwasp /repos/miniwasp \
    && cd /repos/miniwasp \
    && git checkout 8af86b8df40196aa358294b731535423caf18e92 \
    && make python

# volumeview - 12/17/21
RUN git clone https://github.com/magland/volumeview /repos/volumeview \
    && cd /repos/volumeview \
    && git checkout c1dddee5b208dfabc5e643f146746abe78ba030b \
    && pip install -e .

# kachery
RUN pip install kachery-client==1.0.21

COPY scripts /scripts
CMD [ "python3", "/scripts/main.py" ]

LABEL version="0.1.0"