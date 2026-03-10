FROM node:22-alpine

WORKDIR /app

COPY web/package.json /app/package.json
RUN npm install

COPY web /app

ENV NEXT_PUBLIC_API_BASE_URL=http://api:8000

CMD ["npm", "run", "dev"]
