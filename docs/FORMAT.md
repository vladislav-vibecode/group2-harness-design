# Формат 1.0.0

`registry.json`: schema_version, sources[]. Каждая source: id=sha256, slide_count, artifacts (relative path → SHA-256), review, visual_qa. Путь source folder — полный SHA-256 байтов, не клиентское имя. Schema JSON документирует контракт; runtime validate реализован stdlib и дополнительно сверяет re-extraction, не требует jsonschema.

`inventory.json`: schema_version, slide_size_emu, slides[], support_parts, limitations. Slides: index (1-based presentation order), native_id, part, hidden, layout/master/theme, palette, color_map, backgrounds (slide→layout→master), shapes[], relationships. Shape ID — путь в XML spTree и группах, уникальный внутри слайда; полная ссылка включает source ID + slide index + shape ID. Native ID отдельно; редактирование исходника может изменить пути, поэтому ссылка всегда source-qualified.

Shape: type/name/label; geometry EMU и raw transform с rotation/flip; fill/stroke/effects/style; colors с базовым и преобразованным RGB; text_body/raw_xml; runs; image hashes/crops; tables/charts; children. Идентификаторы XML сохраняются, а не «чинятся». Текст нужен только как label. Geometry отсутствует у некоторых placeholders и может наследоваться. Shape label/table text являются приватными.

Все вложенные native shapes групп извлекаются рекурсивно. Графическая структура SmartArt и vendor extensions остаются в raw XML и оригинале: они не объявляются обычными p:sp. Табличные ячейки записаны как XML table children, а не фиктивные shapes; charts имеют relationships и сохранённые chart XML. Master/layout objects сохраняются в support XML, без притворной нормализации в slide coordinates.

Изображения не дублируются отдельными файлами: доступны в immutable PPTX по part, с хешем и crop. `blipFill` и фон сохранены в raw XML. Theme font refs (`+mj-lt`, `+mn-lt`) не подменяются случайным installed font. Цветовые transforms, alpha и неизвестные свойства сохраняются даже без resolved RGB.

`tokens.json`: method, categories с candidate value/count/provenance. Count — число XML-вхождений, не число слайдов; повторы provenance допустимы. Отдельные категории geometry off/ext, font family/size и colors. Размеры не округляются к «красивой» сетке; роли/семантика не выдумываются.

`docs/ELEMENTS.md` внутри приватного source — подробная сериализация геометрии и оформления всех слайдов и shapes, не только outline текста. Публичного клиентского каталога здесь намеренно нет. Все unsupported детали доступны через raw_xml и original ZIP.
