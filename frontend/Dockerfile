# Используем базовый образ Node.js для сборки
FROM node:18 as build

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем package.json и package-lock.json из папки frontend для установки зависимостей
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все файлы приложения из папки frontend
COPY / ./

# Собираем приложение для продакшн-режима
RUN npm run build

# Используем nginx для сервировки статических файлов
FROM nginx:alpine

# Копируем собранные файлы React-приложения из предыдущего этапа в папку nginx
COPY --from=build /app/build /usr/share/nginx/html

# Экспонируем порт 80 для доступа к приложению
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]