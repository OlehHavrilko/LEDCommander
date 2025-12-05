# Архитектура драйверов LED устройств

## Обзор

Приложение переведено на архитектуру драйверов для поддержки множества протоколов LED-контроллеров (ELK-BLEDOM, Triones, MagicHome, Tuya и др.) через единый интерфейс.

## Структура

```
ledcontrol/
├── interfaces/
│   └── device_interface.py    # Абстрактный интерфейс AbstractLedDevice
├── drivers/
│   ├── elk_bledom.py          # Драйвер ELK-BLEDOM
│   └── device_factory.py      # Фабрика драйверов с fingerprinting
├── ble_controller.py           # Контроллер BLE (использует драйверы)
└── models.py                  # DeviceConfig с полем protocol
```

## Абстрактный интерфейс

Все драйверы наследуются от `AbstractLedDevice` и реализуют:

- `connect(client)` - подключение к устройству
- `disconnect()` - отключение
- `set_color(r, g, b)` - установка RGB цвета
- `set_brightness(brightness)` - яркость (0-100)
- `set_mode(mode_id, speed)` - режим эффекта
- `get_write_characteristic_uuid()` - UUID для записи
- `get_protocol_name()` - название протокола
- `can_handle_device(name, uuids)` - проверка совместимости (статический)
- `get_supported_modes()` - словарь режимов (статический)

## Использование

### Явное указание протокола

В `led_config.json`:

```json
{
  "device": {
    "target_mac": "FF:FF:10:69:5B:2A",
    "write_char_uuid": "0000fff3-0000-1000-8000-00805f9b34fb",
    "protocol": "elk_bledom"
  }
}
```

Доступные протоколы:
- `"elk_bledom"` или `"elk"` или `"bledom"` - ELK-BLEDOM
- `"triones"` - Triones
- `"magichome"` или `"magic_home"` или `"magic"` - MagicHome
- `"tuya"` - Tuya

### Автоматическое определение

Если `protocol` не указан или равен `null`, система автоматически определяет протокол по:
- Имени устройства (например, "ELK", "BLEDOM")
- Рекламируемым UUID сервисов
- Паттернам MAC-адреса

```json
{
  "device": {
    "target_mac": "FF:FF:10:69:5B:2A",
    "protocol": null
  }
}
```

## Добавление нового драйвера

### 1. Создать класс драйвера

```python
# drivers/new_protocol.py
from interfaces.device_interface import AbstractLedDevice

class NewProtocolDriver(AbstractLedDevice):
    WRITE_CHAR_UUID = "0000xxxx-0000-1000-8000-00805f9b34fb"
    
    @staticmethod
    def can_handle_device(device_name, service_uuids):
        # Логика определения устройств
        return "NEWPROTOCOL" in (device_name or "").upper()
    
    # Реализовать все абстрактные методы...
```

### 2. Зарегистрировать в фабрике

```python
# drivers/device_factory.py
from drivers.new_protocol import NewProtocolDriver

_DRIVER_REGISTRY["new_protocol"] = NewProtocolDriver
_DETECTION_ORDER.append(NewProtocolDriver)
```

**Примечание**: Triones, MagicHome и Tuya драйверы уже реализованы и зарегистрированы.

## Поддерживаемые драйверы

### ELK-BLEDOM

- **UUID записи**: `0000fff3-0000-1000-8000-00805f9b34fb`
- **Формат пакета**: `[0x7E, 0x07, 0x05, CMD, P1, P2, P3, SPEED, 0xEF]`
- **Команда цвета**: `CMD=0x03, P1=R, P2=G, P3=B`
- **Команда режима**: `CMD=0x04, P1=mode_id`
- **Режимы**: MANUAL (0x01), CPU (0x02), BREATH (0x03), RAINBOW (0x04)

### Triones

- **UUID записи**: `0000ffd9-0000-1000-8000-00805f9b34fb` (альтернатива: `0000ffd5...`)
- **Формат пакета**: `[0x56, 0xAA, CMD, P1, P2, P3, 0xAA, 0xAA]`
- **Команда цвета**: `CMD=0x01, P1=R, P2=G, P3=B`
- **Команда режима**: `CMD=0x04, P1=mode_id, P2=speed`
- **Режимы**: STATIC (0x01), JUMP (0x02), FADE (0x03), FLASH (0x04)

### MagicHome

- **UUID записи**: `0000ffe5-0000-1000-8000-00805f9b34fb` (альтернатива: `0000ffe9...`)
- **Формат пакета**: `[0x7E, LEN, CMD, DATA..., 0xEF]`
- **Команда цвета**: `CMD=0x05, DATA=[R, G, B, W]`
- **Команда режима**: `CMD=0x04, DATA=[mode_id, speed, ...]`
- **Режимы**: STATIC (0x01), JUMP (0x02), FADE (0x03), FLASH (0x04)

### Tuya

- **UUID записи**: `0000fe95-0000-1000-8000-00805f9b34fb` (альтернатива: `0000fe40...`)
- **Формат пакета**: `[CMD, LEN, DATA...]` (упрощенный вариант)
- **Команда цвета**: `CMD=0x01, DATA=[R, G, B]`
- **Команда режима**: `CMD=0x02, DATA=[mode_id, speed]`
- **Режимы**: STATIC (0x01), JUMP (0x02), FADE (0x03), FLASH (0x04)

**Примечание**: Tuya протокол может использовать шифрование для некоторых устройств. Базовая реализация поддерживает простые незашифрованные команды.

## Изменения в коде

### BleDeviceController

- Использует `DeviceFactory` для создания драйверов
- Вызывает методы драйвера вместо прямых BLE команд
- Автоматически определяет протокол при сканировании

### DeviceConfig

- Добавлено поле `protocol: Optional[str]`
- `write_char_uuid` теперь опциональный (заполняется из драйвера)

## Обратная совместимость

- Старые конфиги без поля `protocol` работают (автоопределение)
- Существующий UI и MVVM связи не изменены
- Все текущие функции сохранены

