FROM node:20-alpine

WORKDIR /app

# Спочатку копіюємо тільки package.json — для кешування шару з залежностями
COPY package.json package-lock.json* ./
RUN npm install

# Тепер копіюємо решту коду
COPY . .

EXPOSE 3000

# Запускаємо Vite dev-сервер, --host потрібен щоб він був доступний ззовні контейнера
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]