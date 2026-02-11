# Project Overview

Проект — каркас для запуска пайплайнов и формирования артефактов для LLM-анализа.

## Цели
- Детерминированная сборка `latest_bundle.zip`.
- Хранение “сжатой памяти проекта” прямо в репозитории.
- Быстрый перенос контекста в новый чат через один архив.

## Ключевые точки
- Конфиг: `config/hub.yaml`.
- Запуск: `python -m pipelines.run_all`.
- Артефакты: `data/ai_contract/latest/latest_bundle.zip` и `run_manifest.json`.
- Memory Pack: `contracts/meta/`.
