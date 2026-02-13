# AGENT_RULES

## Primary context
- Агент обязан считать `latest_bundle.zip` основным переносимым контекстом проекта.
- При работе в репозитории правила берутся из `AGENTS.md` и `.agents/skills/*`.

## Execution protocol
1. Сначала preflight (без патча).
2. Затем implement в согласованном scope.
3. Затем verify по acceptance-командам.

## Track discipline
- Следовать трекам `PR-A*`, `PR-F*`, `PR-G*`.
- Избегать cross-track изменений.
- При конфликте правил — выбирать более строгий вариант и явно сообщать причину.

## Quality bar
- Детерминизм и повторяемость важнее “магии”.
- Короткая диагностика вместо шумных логов.
- Никаких placeholder-артефактов и фиктивных путей.

## Operator queue preference
- Где возможно, оформлять работу через `tools/operator/**` как очередь задач/патчей для прозрачного handoff.
