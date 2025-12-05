# Чеклист отладки и тестирования

## ✅ Выполнено

### Структура проекта
- ✅ Все файлы созданы в правильных папках
- ✅ Импорты обновлены
- ✅ Синтаксис проверен

### Тесты
- ✅ `test_structure_only.py` - проверка структуры файлов
- ✅ `test_imports.py` - проверка импортов (требует venv)
- ✅ `test_exe.py` - проверка собранного EXE

### Сборка
- ✅ `build.py` создан и настроен
- ✅ EXE собран: `dist/Commander.exe`

## Тестирование

### 1. Проверка структуры (без зависимостей)
```bash
python test_structure_only.py
```

### 2. Проверка импортов (требует venv)
```bash
.\venv\Scripts\Activate.ps1
python test_imports.py
```

### 3. Проверка EXE
```bash
python test_exe.py
```

### 4. Запуск приложения (для отладки)
```bash
.\venv\Scripts\Activate.ps1
python main.py
```

### 5. Запуск EXE
```bash
.\dist\Commander.exe
```

## Возможные проблемы и решения

### Проблема: "ModuleNotFoundError: bleak"
**Решение**: Активировать venv и установить зависимости:
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Проблема: EXE не запускается
**Проверить**:
1. Консоль открыта? (--console в build.py)
2. Логи в `led_control.log`
3. Запустить из командной строки для просмотра ошибок

### Проблема: Импорты не работают в EXE
**Решение**: 
- Проверить `--add-data=core;core` и `--add-data=ui;ui` в build.py
- Убедиться, что все модули в правильных папках

### Проблема: UI не отображается
**Проверить**:
1. CustomTkinter установлен
2. `--collect-all=customtkinter` в build.py
3. Запустить с консолью для просмотра ошибок

## Отладка

### Включить консоль в EXE
В `build.py` использовать `--console` вместо `--windowed`

### Просмотр логов
```bash
type led_control.log
```

### Проверка зависимостей в EXE
Использовать PyInstaller для анализа:
```bash
pyi-archive_viewer dist\Commander.exe
```

## Следующие шаги

1. ✅ Структура создана
2. ✅ Тесты написаны
3. ✅ EXE собран
4. ⏳ Тестирование EXE (вручную)
5. ⏳ Исправление найденных ошибок

