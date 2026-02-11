# contracts/meta/START_HERE

## Что читать в первую очередь
1. `contracts/meta/AGENT_RULES.md`
2. `contracts/meta/project_state.yml`
3. `contracts/meta/COMPILED_MEMORY.md`

## Быстрый алгоритм восстановления контекста
1. Прочитать правила и ограничения (`AGENT_RULES.md`).
2. Проверить актуальное состояние проекта (`project_state.yml`).
3. Прочитать консолидированную память (`COMPILED_MEMORY.md`).
4. Открыть `pipelines/run_all.py` и `config/hub.yaml`.

## Локальный запуск
```bash
python -m pip install -r requirements.txt
python -m pipelines.run_all
```
