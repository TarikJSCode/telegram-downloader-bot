# Вихідне Python-середовище
FROM python:3.10-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо залежності
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо всі файли
COPY . .

# Виставляємо порт (для webhook, потрібен для fly)
ENV PORT=8080

# Запускаємо бот
CMD ["python", "main.py"]
