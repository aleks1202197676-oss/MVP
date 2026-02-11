# PATCH NOTES

## Что изменено

1. Добавлен скрипт `scripts/verify_bundle.py` (stdlib-only) для проверки обязательных путей внутри `latest_bundle.zip`.
2. В CI (`.github/workflows/ci.yml`) шаг проверки bundle переведён с inline Python на вызов `python scripts/verify_bundle.py data/ai_contract/latest/latest_bundle.zip`.
3. Из `unified_hub_starter.zip` извлечена папка `00__CLICK_HERE/` в корень репозитория.
4. Корневые `.cmd`-файлы помечены как deprecated и проксируют вызовы в `00__CLICK_HERE/` для снижения путаницы.

## Проверки

- Локально: `python -m pipelines.run_all`
- Локально: `python scripts/verify_bundle.py`
