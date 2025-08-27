# 🤖 Алиса + DeepSeek

Навык для Яндекс.Алисы, который подключается к API DeepSeek через FastAPI.

## 🚀 Как запустить

### 1. Получить API ключ
- Зарегистрируйся на https://platform.deepseek.com/
- Скопируй свой API KEY (например, `sk-xxxx`)

### 2. Залить на Render
1. Форкни этот репозиторий или скопируй его в свой GitHub.
2. Перейди на https://render.com
3. Нажми **New → Web Service**
4. Подключи свой GitHub-репозиторий.
5. Настройки:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000`
6. В разделе Environment добавь переменную:
   - Key: `DEEPSEEK_API_KEY`
   - Value: `твой_ключ`

После деплоя Render даст ссылку вида:
```
https://deepseek-alisa.onrender.com/
```

### 3. Подключить в Алису
1. Иди в https://dialogs.yandex.ru/developer
2. Создай новый **Навык → Диалог**
3. В поле **Webhook URL** вставь ссылку от Render.
4. Сохрани и активируй навык.

### 4. Проверка
Скажи колонке:
```
Алиса, запусти DeepSeek
```
Теперь Алиса отвечает через DeepSeek 🚀
