FROM python:3.14-trixie AS deb_build_base

RUN apt-get update
RUN apt-get install -y binutils
RUN apt-get install -y libopencv-dev
RUN apt-get install -y python3-opencv
RUN apt-get install -y libxcb-cursor0

FROM deb_build_base

RUN mkdir /build
COPY ./ /build/
WORKDIR /build
