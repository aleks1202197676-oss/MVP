# chats

Store only compact cross-chat summaries used to restore project context.
Do not store full chat exports in this folder.

## Anti-mixing rule (mandatory)
- Each summary file MUST have exactly one `project_id`.
- Never combine updates from different projects in the same summary.
- If a chat covered multiple projects, split it into one file per `project_id`.

## Recommended summary header

```md
# chat_summary: <date_or_id>
project_id: <project_id>
tracks: [A]
source_chat: <link_or_note>

## Context restored
- ...

## Decisions
- ...

## Remaining work
- ...

## Next steps
- ...
```

## Retention guidance
- Keep only the most useful 3–6 summaries per active project.
- Prefer summaries that capture decisions, risks, and unfinished tasks.
