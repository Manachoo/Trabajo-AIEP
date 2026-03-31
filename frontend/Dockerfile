# Etapa 1: Construcción de la aplicación
FROM node:20-alpine AS build

# Establece el directorio de trabajo
WORKDIR /app

# Copia el package.json y package-lock.json
COPY package*.json ./

# Instala las dependencias
RUN npm install

# Copia el resto de los archivos de la aplicación
COPY . .

# Construye la aplicación para producción
RUN npm run build

# Etapa 2: Servir la aplicación con Nginx
FROM nginx:stable-alpine

# Copia los archivos construidos desde la etapa de 'build'
COPY --from=build /app/dist /usr/share/nginx/html


# Expone el puerto 80
EXPOSE 80

# El comando por defecto de Nginx se encargará de servir los archivos
CMD ["nginx", "-g", "daemon off;"]
