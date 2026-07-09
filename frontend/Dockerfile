FROM node:20-alpine AS build
WORKDIR /app

# Copy all frontend files
COPY . .

# Install dependencies
RUN npm install

# Build the app
ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Serve with nginx
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE ${PORT:-80}
CMD ["sh", "-c", "sed -i 's/listen 80;/listen ${PORT:-80};/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
