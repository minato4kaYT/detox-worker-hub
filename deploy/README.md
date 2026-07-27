# DETOX — деплой демо-флота (Onyx Hub)

⚠️ Демонстрационный проект. Все боты, бренды и данные вымышленны.
Отрисовщик наносит водяной знак «ДЕМО» на каждое изображение.

## Боты
| Юнит | Модуль | Токен из .env | Роль |
|------|--------|---------------|------|
| detox-hub     | `hub.run`    | `HUB_TOKEN`    | воркер-хаб (анкеты, кураторы, DTC) |
| detox-trade   | `trade.run`  | `TRADE_TOKEN`  | демо MEXC-трейд |
| detox-escort  | `escort.run` | `ESCORT_TOKEN` | демо Violet Agency |
| detox-draw    | `draw.run`   | `DRAW_TOKEN`   | демо-отрисовщик «чеков» |

## Установка
1. `pip install -r /root/detox/requirements.txt`
2. Впиши токены демо-ботов в `/root/detox/.env` (создай через @BotFather).
3. `python /root/detox/seed.py`  — наполнить справочники (кураторы и т.п.).
4. Скопируй юниты и запусти:
   ```
   cp /root/detox/deploy/detox-*.service /etc/systemd/system/
   systemctl daemon-reload
   systemctl enable --now detox-hub detox-trade detox-escort detox-draw
   ```
5. Логи: `journalctl -u detox-draw -f`

## Локальный запуск (без systemd)
```
cd /root/detox
python -m draw.run     # или hub.run / trade.run / escort.run
```
