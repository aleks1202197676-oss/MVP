# Finance MVP variables dictionary

- `horizon_days`: горизонт симуляции в днях.
- `start_date`: старт симуляции.
- `allocation_policy`: политика аналитического разнесения платежа по товарам в долге.
- `allow_pay_ahead`: разрешение платить до дедлайна.
- `price_mode`:
  - `fixed`: использовать `price_value`.
  - `range`: использовать верхнюю границу `price_max` (консервативно).
- `chosen_source`: выбранный источник покупки (`card*`, `cash`, `split`, `installment`).
- `deadline_date`: дедлайн погашения обязательства по товару.
- `remaining_balance`: остаток долга по товару.
- `in_grace_bool`: индикатор нахождения карты в grace-периоде относительно ближайшего дедлайна.
- `violations`: события нарушения ограничений (лимит/просрочка).
