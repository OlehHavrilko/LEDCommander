# LED CONTROL v2.1 — RGB LED Manager via Bluetooth

Настольное приложение для управления RGB LED-лентой через BLE (Bluetooth Low Energy) с поддержкой режимов, пресетов, HEX-кодов и логирования.

## Функции

- ✅ **RGB Слайдеры** — точная настройка цвета
- ✅ **9 Цветовых пресетов** — быстрая смена палитры
- ✅ **HEX/RGB ввод** — вставка кодов типа `#FF5500`
- ✅ **Яркость** — общий регулятор от 0% до 100%
- ✅ **3 Интеллектуальных режима**:
  - **CPU Monitor** — подсветка следует за нагрузкой процессора (Синий → Красный)
  - **Neon Breath** — плавное дыхание фиолетовым неоном
  - **Rainbow Cycle** — полный цикл радуги
- ✅ **Сохранение конфига** — автосохранение цвета и яркости (`led_config.json`)
- ✅ **Логирование** — полный лог событий и ошибок в `led_control.log`
- ✅ **Переподключение** — автоматическая переподключение при потере связи

## Системные требования

- **OS**: Windows 10/11 (Bluetooth требуется)
- **Python**: 3.8+
- **Зависимости**: customtkinter, bleak, psutil

## Установка

### 1. Клонировать репозиторий
```bash
git clone <repo_url>
cd ledcontrol
```

### 2. Создать виртуальное окружение
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Установить зависимости
```powershell
pip install -r requirements.txt
```

## Запуск

```powershell
# Активировать venv (если не активирован)
.\venv\Scripts\Activate.ps1

# Запустить приложение
python main.py
```

## Сборка в EXE

Используйте скрипт `build.py`:

```powershell
# Установить PyInstaller (если не установлен)
pip install pyinstaller

# Собрать EXE
python build.py

# Результат: dist/Commander.exe
```

## Конфигурация

Все параметры хранятся в `led_config.json`:

```json
{
  "target_mac": "FF:FF:10:69:5B:2A",
  "write_char_uuid": "0000fff3-0000-1000-8000-00805f9b34fb",
  "last_color": {"r": 255, "g": 255, "b": 255},
  "brightness": 1.0,
  "theme": "Dark"
}
```

**Как изменить MAC-адрес устройства:**
1. Используйте приложение `nRF Connect` (для Windows)
2. Найдите ваше BLE-устройство и скопируйте MAC
3. Отредактируйте `led_config.json` или измените `TARGET_MAC` в коде

## Интерфейс

### Вкладка "PALETTE"
- Регулятор яркости
- 9 цветовых кнопок (быстрые пресеты)
- HEX-ввод для вставки кодов типа `#FF5500`
- RGB-слайдеры для тонкой настройки

### Вкладка "MODES"
- **Ryzen CPU Monitor** — подсветка реагирует на загруженность процессора
- **Neon Breath** — плавная пульсирующая анимация
- **Rainbow Cycle** — циклический проход по радуге
- **Stop Effects (MANUAL)** — отключить режимы, использовать ручное управление

### Вкладка "SETTINGS"
- Показать целевой MAC-адрес
- **Force Reconnect** — переподключиться к устройству
- **Save Preferences** — сохранить текущие настройки
- **View Log File** — открыть логи для отладки

## Логирование

Все события записываются в `led_control.log`:
- Подключение/отключение
- Смена режимов
- Ошибки BLE
- Применение цветов

Используйте вкладку **Settings → View Log File** для просмотра.

## Примеры использования

### Изменить цвет через HEX
1. Перейти на вкладку **PALETTE**
2. В поле **HEX COLOR** ввести `#FF00FF` (розовый)
3. Нажать **APPLY**

### Использовать режим CPU Monitor
1. Перейти на вкладку **MODES**
2. Нажать **RYZEN CPU MONITOR**
3. Цвет будет менять от синего (холодная нагрузка) к красному (горячая)

### Сохранить текущий цвет
1. Отрегулировать желаемый цвет
2. Перейти на **SETTINGS**
3. Нажать **SAVE PREFERENCES**
4. При следующем запуске цвет восстановится автоматически

## Структура проекта

```
ledcontrol/
├── core/                  # Бизнес-логика (независима от UI)
│   ├── models.py         # Модели данных
│   ├── services.py       # Сервисы (Config, Logger)
│   ├── interfaces.py     # Абстрактный интерфейс драйверов
│   ├── controller.py     # BLE контроллер
│   └── drivers/          # Драйверы протоколов (ELK-BLEDOM, Triones, etc.)
│
├── ui/                    # Пользовательский интерфейс
│   ├── main_window.py    # Главное окно
│   ├── components.py     # UI компоненты
│   └── viewmodels.py     # ViewModel (мост UI ↔ Core)
│
├── tests/                 # Тесты
├── docs/                  # Документация
│
├── main.py               # Точка входа приложения
├── build.py              # Скрипт сборки EXE
├── requirements.txt      # Зависимости
└── README.md             # Этот файл
```

Подробнее см. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) и [docs/](docs/).

## Поиск и устранение неисправностей

### "Device not found"
- Убедитесь, что устройство включено
- Проверьте MAC-адрес в `led_config.json`
- Используйте nRF Connect для сканирования доступных устройств

### "Bluetooth radio is not powered on"
- Включите Bluetooth в Windows Settings
- На ноутбуке нажмите комбинацию для включения Bluetooth или используйте физический переключатель

### "CONNECTION LOST"
- Приложение автоматически переподключится
- Если это часто происходит, используйте **Force Reconnect** на вкладке Settings

### Нет импорта customtkinter
```powershell
pip install customtkinter
```

## Заметки для разработчиков

- `BleController` работает в отдельном asyncio loop в фоновом потоке
- GUI обновления всегда идут через главный поток (используется `self.after()`)
- Payload для отправки: `bytearray([0x7E, 0x07, 0x05, 0x03, r, g, b, 0x10, 0xEF])`
- UUID для записи конфигурируется в `led_config.json`

## Лицензия

MIT

## Автор

Developed for custom BLE LED controllers with Ryzen CPU monitoring support.
