FROM node:20

WORKDIR /app

COPY package.json webpack.config.js ./
RUN npm install

COPY public ./public
COPY src ./src
COPY server.js ./

RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
