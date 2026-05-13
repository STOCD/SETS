FROM deb_build_base

RUN mkdir /build
COPY ./ /build/
WORKDIR /build
