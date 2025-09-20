# Family Planner Bot

**Удобный Telegram-бот для планирования семейных событий, уведомлений и синхронизации с Google Calendar.**

---

## 📌 Описание проекта

**Family Planner Bot** — это инструмент для управления семейными событиями, который позволяет:
- Создавать, редактировать и удалять события.
- Настраивать уведомления о событиях.
- Синхронизировать события с Google Calendar.
- Получать еженедельные резюме событий в семейном чате.
- Работать с личным и семейным календарём.

---

## 🛠 Технологии

- **Язык:** Python 3.11
- **Фреймворк:** [aiogram](https://docs.aiogram.dev/) 3.22.0
- **База данных:** SQLite
- **Google API:** `google-api-python-client`, `google-auth-oauthlib`
- **Планировщик задач:** `APScheduler`
- **Дополнительные библиотеки:** `environs`, `aiogram-calendar`, `SQLAlchemy`

---

## 📦 Структура проекта

```plaintext
bot/
├── google/
│   ├── credentials.json
│   └── token.json
├── handlers/
├── keyboards/
├── middlewares/
├── models/
├── services/
├── utils/
├── config.py
└── main.py
database/
└── family_planner.db
.env
.env.example
README.md
requirements.txt
.gitignore
```

---

## 🚀 Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-repo/family-planner-bot.git
cd family-planner-bot
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Настройка `.env` файла

Создайте файл `.env` на основе `.env.example` и заполните его:

```plaintext
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321
GOOGLE_CALENDAR_ID=your_calendar_id
```

### 4. Настройка Google Calendar API

1. Скачайте `credentials.json` из [Google Cloud Console](https://console.cloud.google.com/).
2. Поместите файл в папку `bot/google/`.
3. Запустите бота, чтобы сгенерировать `token.json`.

### 5. Запуск бота

```bash
python bot/main.py
```

---

## 🤖 Команды бота

| Команда               | Описание                                      |
|-----------------------|-----------------------------------------------|
| `/start`              | Запуск бота и главное меню                    |
| `Новое событие`       | Создать новое событие                         |
| `Мои события`         | Просмотр личных событий                       |
| `Семейный календарь`  | Просмотр событий всей семьи                  |
| `Настройки`           | Настройка уведомлений и других параметров     |

---

## 📂 Работа с базой данных

### Резервное копирование

Бот автоматически создаёт резервные копии базы данных каждый день в 3:00. Старые копии (старше 30 дней) удаляются.

### Восстановление

Чтобы восстановить базу данных из резервной копии, скопируйте нужный файл из папки `backups/` в `database/family_planner.db`.

---

## 📝 Лицензия

Проект распространяется под лицензией **MIT**.

---

## 📧 Контакты

По вопросам и предложениям: mr.paralaks@gmail.com

---

**Спасибо за использование Family Planner Bot!** 🎉
