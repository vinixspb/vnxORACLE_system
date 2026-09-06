"""
vnxORACLE — Форматирование ответов модели под Telegram HTML
==========================================================
Модель отвечает в Markdown, а сообщения уходят с parse_mode='HTML'.
Без конвертации пользователь видит сырые «**звёздочки**».

Telegram HTML поддерживает ограниченный набор тегов, заголовков среди них
нет — поэтому «### Заголовок» становится <b>Заголовок</b>.
"""

import html
import re

# Блоки кода вырезаем перед конвертацией: внутри них Markdown не работает.
_FENCED = re.compile(r"```(\w*)\n?(.*?)```", re.DOTALL)
_INLINE_CODE = re.compile(r"`([^`\n]+)`")

_BOLD = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_BOLD_ALT = re.compile(r"__(.+?)__", re.DOTALL)
# Курсив: одиночная звёздочка, не являющаяся частью ** и не маркером списка
_ITALIC = re.compile(r"(?<![\*\w])\*(?!\s)([^\*\n]+?)(?<!\s)\*(?!\*)")
_ITALIC_ALT = re.compile(r"(?<![_\w])_(?!\s)([^_\n]+?)(?<!\s)_(?!_)")
_STRIKE = re.compile(r"~~(.+?)~~", re.DOTALL)
_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")

_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*$", re.MULTILINE)
_BULLET = re.compile(r"^(\s*)[-*+]\s+(?=\S)", re.MULTILINE)
_HR = re.compile(r"^\s*([-*_])(?:\s*\1){2,}\s*$", re.MULTILINE)


def md_to_html(text: str) -> str:
    """Markdown от модели -> HTML, безопасный для Telegram."""
    if not text:
        return ""

    placeholders = []

    def _stash(rendered: str) -> str:
        placeholders.append(rendered)
        return f"\x00{len(placeholders) - 1}\x00"

    def _fenced(m):
        lang, body = m.group(1), m.group(2)
        code = html.escape(body.strip("\n"))
        cls = f' class="language-{lang}"' if lang else ""
        return _stash(f"<pre><code{cls}>{code}</code></pre>")

    def _inline(m):
        return _stash(f"<code>{html.escape(m.group(1))}</code>")

    text = _FENCED.sub(_fenced, text)
    text = _INLINE_CODE.sub(_inline, text)

    # Вне блоков кода экранируем всё, что могло бы сойти за разметку
    text = html.escape(text)

    text = _HR.sub("—" * 12, text)
    text = _HEADING.sub(r"<b>\1</b>", text)
    text = _LINK.sub(r'<a href="\2">\1</a>', text)
    text = _BOLD.sub(r"<b>\1</b>", text)
    text = _BOLD_ALT.sub(r"<b>\1</b>", text)
    text = _STRIKE.sub(r"<s>\1</s>", text)
    text = _ITALIC.sub(r"<i>\1</i>", text)
    text = _ITALIC_ALT.sub(r"<i>\1</i>", text)
    text = _BULLET.sub(r"\1• ", text)

    # Три и более пустых строки подряд -> одна
    text = re.sub(r"\n{3,}", "\n\n", text)

    for i, rendered in enumerate(placeholders):
        text = text.replace(f"\x00{i}\x00", rendered)

    return text.strip()
