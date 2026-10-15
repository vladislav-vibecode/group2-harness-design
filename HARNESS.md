# Harness: ingest → extract → classify → review → version → reuse → QA

## 1. Ingest
`python3 harness.py ingest /path/to/source.pptx`.
Файл остаётся локальным. SHA-256 полных байтов — immutable source ID. Изменённая версия создаёт новую запись, даже если имя совпало. Повтор тех же байтов валидирует существующую запись. Незарегистрированный каталог с тем же ID — ошибка, не повод к overwrite. Не удалять конфликт автоматически.

## 2. Extract
Сохранить все native shapes рекурсивно, полный XML и source-qualified происхождение. Нулевые и отрицательные координаты допустимы: off-canvas декор не удалять. В группах `off/ext/chOff/chExt` описывают transform, не мировую геометрию. Элементы master/layout сохраняются как support XML; slide shapes перечисляются отдельно. Исходные XML и PPTX позволяют проверить неполную нормализацию.

## 3. Classify
Статистика прямых XML-вхождений образует candidates с provenance; цвета разных ролей не объединять в семантическую палитру без review. Отдельная ручная классификация: заголовок/фон/карточка/таблица/диаграмма/декор/изображение; допустимо unknown. Не анализировать результаты бизнеса и copy.

## 4. Review
Рендер всех слайдов включая hidden; проверить число страниц против inventory. Сохранить reviewer, дату, renderer/version, substitutions и проверенные slide IDs в отдельном приватном review. Если renderer недоступен — structural-only, visual QA pending. `private/visual-review/` независим от extractor, не перезаписывать. Изменение review не меняет immutable source artifacts.

## 5. Version
Схема имеет semantic version; incompatible изменение major. Никаких автоматических миграций inplace: новая библиотека/derived version с source link. `registry.json` содержит artifact hashes и состояния. Ручные решения хранить отдельно от source folder. Candidate conflicts — source-qualified варианты, не blind overwrite. Повышение candidate до approved требует reviewer evidence, это пока ручной процесс, не команда CLI.

## 6. Reuse
Выбрать approved pattern по композиции/типографике/геометрии, а не по маркетинговому содержанию. Выписать source ID, slide index, shape paths и какие свойства переносятся. Не копировать защищённые активы в публичные примеры.

## 7. QA
`python3 harness.py validate`; `python3 -m unittest discover -s tests -v`. Сверить rendering отдельно. Перед передачей выполнить `python3 scripts/package.py`; public ZIP строится только из allowlist. Private ZIP содержит клиентские данные: не публиковать. Архиватор проверяет имена и байты каждого упакованного файла. Не выполнять push и не менять глобальные skills.
