---
name: presentation-design-library
description: Extract and reuse private presentation design evidence.
version: 0.1.0
author: Vladislav, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [presentation, design, library, evidence]
    related_skills: []
---

# Presentation Design Library

Локальная пополняемая библиотека дизайна. Без сети, маркетингового анализа и глобальной установки навыка. Python standard library.

## When to Use
- Добавить локальный PPTX как дизайн-источник.
- Изучить все элементы, геометрию, стили и происхождение кандидатов токенов.
- Повторно использовать проверенную композицию с сохранением traceability.
- Не использовать для анализа бизнес-результатов, переписывания copy или публикации клиентских данных.

## Prerequisites
Работать из корня этого репозитория. Исходник предоставить локально; не искать секреты, Keychain или облачный конвертер. Приватная библиотека по умолчанию `private/library`. Публичный skill содержит только относительные пути.

## How to Run
Через `terminal` из корня репозитория:

```python
terminal(command='python3 harness.py ingest /path/to/local-source.pptx')
terminal(command='python3 harness.py validate')
terminal(command='python3 harness.py stats')
terminal(command='python3 -m unittest discover -s tests -v')
terminal(command='python3 scripts/package.py')
```

## Procedure
1. Прочитать `HARNESS.md`, `DESIGN.md`, `docs/FORMAT.md` через `read_file`. Убедиться, что scope только дизайн.
2. Ingest исходника. Проверить source SHA-256 ID и slide count; сохранить исходник неизменным.
3. Читать `private/library/registry.json`, затем `sources/<id>/inventory.json`, `tokens.json`, `docs/ELEMENTS.md` через `read_file`. Учесть рекурсивные группы, crops и наследование; null не превращать в default.
4. Для ролей и approved patterns выполнить visual review всех слайдов, включая hidden. Проверить `private/visual-review/VISUAL-DESIGN.md`, если существует; не перезаписывать чужой review. При отсутствии рендера явно оставить visual pending.
5. Ручную классификацию и решения хранить вне immutable source folder с source-qualified provenance; кандидаты не считать утверждёнными токенами.
6. При конфликте остановить запись. Не overwrite: разные байты — новый ID, одинаковые — проверка существующего. Слияние имён требует отдельного review; schema major mismatch требует явной миграции в новую библиотеку.
7. До reuse указать конкретные slide/shape refs и список переносимых свойств. Не копировать приватный label в public docs.
8. Выполнить validate, tests, package; проверить содержимое public ZIP и git diff. Никогда не push без отдельного запроса.

## Pitfalls
Статистика XML не заменяет visual inspection. Group geometry локальная. Font/style cascade не полностью resolved: raw theme/master/layout остаются evidence. Missing property значит inherited/unresolved. Chart XML не повод придумывать значения. Contact sheets не доказывают читаемость всех мелких надписей.

## Verification
CLI validate должен завершиться с кодом 0; все unittest пройти. Подробный каталог должен иметь раздел для каждого слайда и recursive shape. Проверить public archive: только allowlist, без private, client source, images, tokens и renders. Ограничения и фактический объём visual review указать в отчёте с абсолютными локальными путями; эти пути не записывать в public skill.

## References
- `HARNESS.md` — lifecycle и конфликты.
- `DESIGN.md` — evidence/candidate/approved.
- `docs/FORMAT.md` — формат и границы разрешения.
- `schemas/registry.schema.json` — публичная схема реестра.
