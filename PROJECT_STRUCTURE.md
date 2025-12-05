# Структура проекта LED COMMANDER v3.0

## 📁 Организация файлов

```
ledcontrol/
├── core/                      # 🧠 Бизнес-логика (независима от UI)
│   ├── __init__.py
│   ├── models.py              # Модели данных (Color, ColorMode, DeviceConfig, etc.)
│   ├── services.py            # Сервисы (ConfigService, LoggerService)
│   ├── interfaces.py          # Абстрактный интерфейс AbstractLedDevice
│   ├── controller.py          # BLE контроллер и мост приложения
│   └── drivers/               # 🔌 Драйверы протоколов
│       ├── __init__.py
│       ├── device_factory.py  # Фабрика драйверов
│       ├── elk_bledom.py      # Драйвер ELK-BLEDOM
│       ├── triones.py          # Драйвер Triones
│       ├── magichome.py       # Драйвер MagicHome
│       └── tuya.py            # Драйвер Tuya
│
├── ui/                        # 🖥️ Пользовательский интерфейс
│   ├── __init__.py
│   ├── main_window.py         # Главное окно приложения
│   ├── components.py          # UI компоненты (виджеты, стили)
│   └── viewmodels.py          # ViewModel (мост UI ↔ Core)
│
├── tests/                     # 🧪 Тесты
│   ├── test_*.py              # Unit и integration тесты
│   ├── run_tests.py           # Скрипт запуска тестов
│   └── validate.py            # Валидация системы
│
├── assets/                    # 🎨 Ресурсы
│   └── (иконки, изображения)
│
├── main.py                    # 🚀 Точка входа приложения
├── build.py                   # ⚙️ Скрипт сборки EXE
├── requirements.txt           # 📦 Зависимости
├── README.md                  # 📖 Документация
└── .gitignore                # 🚫 Игнорируемые файлы
```

## 📚 Документация

- **README.md** - Основная документация
- **ARCHITECTURE.md** - Архитектура системы
- **PROJECT_STRUCTURE.md** - Этот файл (структура проекта)
- **BUILD_REPORT.md** - Отчет о сборке
- **DEBUG_CHECKLIST.md** - Чеклист отладки

## 🔄 Импорты

### Core модули
```python
from core.models import Color, ColorMode, DeviceConfig
from core.services import ConfigService, LoggerService
from core.interfaces import AbstractLedDevice
from core.controller import BleDeviceController, BleApplicationBridge
from core.drivers.device_factory import DeviceFactory
```

### UI модули
```python
from ui.main_window import DashboardView
from ui.components import ColorWheelPicker, NavButton
from ui.viewmodels import Application
```

## 🚀 Запуск

### Разработка
```bash
# Активировать виртуальное окружение
.\venv\Scripts\Activate.ps1

# Запустить приложение
python main.py
```

### Тестирование
```bash
# Запустить все тесты
python -m pytest tests/

# Проверить структуру
python tests/validate.py
```

### Сборка
```bash
# Собрать EXE
python build.py

# Результат: dist/Commander.exe
```

## 📝 Примечания

- Все старые файлы удалены (models.py, services.py, ble_controller.py, ui.py, app.py)
- Старые папки удалены (drivers/, interfaces/)
- Все импорты обновлены на новую структуру
- Тесты перемещены в tests/

