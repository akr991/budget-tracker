FROM node:20-alpine AS build
WORKDIR /app

# Copy all frontend files
COPY frontend/ .

# Install dependencies
RUN npm install

# Build the app
ARG VITE_API_URL=http://localhost:8000/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# Serve with nginx
FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
