# Use a lightweight Node.js image
FROM node:20.18.3-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install
RUN npm install zustand

# Copy the rest of the application files
COPY . .

# Build the app for production
RUN npm run build

# Use an Nginx server to serve the built frontend
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
