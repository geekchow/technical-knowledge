FROM public.ecr.aws/lambda/nodejs:16

WORKDIR "/function"

COPY src ./src

COPY package.json ./

RUN npm ci

RUN npm run build

ENV NODE_ENV="production"


