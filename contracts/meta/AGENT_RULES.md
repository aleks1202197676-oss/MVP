# AGENT_RULES

- Всегда начинать с `contracts/meta/project_state.yml` и `contracts/meta/COMPILED_MEMORY.md`.
- Сохранять детерминированность: стабильный порядок файлов и секций.
- После успешного прогона обновлять `project_state.yml` и `COMPILED_MEMORY.*`.
- Собирать `latest_bundle.zip` как переносимый контекст: память + ключевой код.
