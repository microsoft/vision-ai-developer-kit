FROM node:10

RUN apt-get update && apt-get install -y \
    ffmpeg

ENV WORKINGDIR /app
WORKDIR ${WORKINGDIR}

ADD package.json ${WORKINGDIR}/package.json
ADD tslint.json ${WORKINGDIR}/tslint.json
ADD tsconfig.json ${WORKINGDIR}/tsconfig.json
ADD src ${WORKINGDIR}/src

RUN npm install -q && \
    ./node_modules/.bin/tsc -p . && \
    ./node_modules/.bin/tslint -p . && \
    npm prune --production && \
    rm -f tslint.json && \
    rm -f tsconfig.json && \
    rm -rf src

EXPOSE 9001

ENTRYPOINT ["node", "./dist/index"]
