# ────────────────────────────────────────────────
#  Make labels show cleanly with the bundled Khmer font (resources/fonts/KhmerDubbedSans.ttf).
#  Kodi's font engine has no fallback font, so any character the font lacks is drawn as a box.
#  clean_label() maps CJK/full-width brackets and punctuation to ASCII and drops symbols the
#  font can't draw (emoji such as 🎥⚡, variation selectors, joiners). Letters are always kept.
#  RANGES = the font's character map; regenerate it if the font file changes.
# ────────────────────────────────────────────────
import re, bisect, unicodedata

RANGES = [
    (0x0000, 0x0000), (0x000D, 0x000D), (0x0020, 0x007E), (0x00A0, 0x0377),
    (0x037A, 0x037F), (0x0384, 0x038A), (0x038C, 0x038C), (0x038E, 0x03A1),
    (0x03A3, 0x03E1), (0x03F0, 0x052F), (0x10FB, 0x10FB), (0x1780, 0x17DD),
    (0x17E0, 0x17E9), (0x17F0, 0x17F9), (0x19E0, 0x19FF), (0x1AB0, 0x1AC0),
    (0x1AC5, 0x1AC5), (0x1AC7, 0x1ACE), (0x1C80, 0x1C88), (0x1D00, 0x1DF9),
    (0x1DFB, 0x1F15), (0x1F18, 0x1F1D), (0x1F20, 0x1F45), (0x1F48, 0x1F4D),
    (0x1F50, 0x1F57), (0x1F59, 0x1F59), (0x1F5B, 0x1F5B), (0x1F5D, 0x1F5D),
    (0x1F5F, 0x1F7D), (0x1F80, 0x1FB4), (0x1FB6, 0x1FC4), (0x1FC6, 0x1FD3),
    (0x1FD6, 0x1FDB), (0x1FDD, 0x1FEF), (0x1FF2, 0x1FF4), (0x1FF6, 0x1FFE),
    (0x2000, 0x2064), (0x2066, 0x2071), (0x2074, 0x208E), (0x2090, 0x209C),
    (0x20A0, 0x20C0), (0x20F0, 0x20F0), (0x2100, 0x215F), (0x2183, 0x2184),
    (0x2189, 0x2189), (0x2212, 0x2212), (0x25CC, 0x25CC), (0x2C60, 0x2C7F),
    (0x2DE0, 0x2E5D), (0xA640, 0xA69F), (0xA700, 0xA7CA), (0xA7D0, 0xA7D1),
    (0xA7D3, 0xA7D3), (0xA7D5, 0xA7D9), (0xA7F2, 0xA7FF), (0xA92E, 0xA92E),
    (0xAB30, 0xAB6B), (0xFB00, 0xFB06), (0xFE00, 0xFE00), (0xFE20, 0xFE2F),
    (0xFEFF, 0xFEFF), (0xFFFC, 0xFFFD), (0x10780, 0x10785), (0x10787, 0x107B0),
    (0x107B2, 0x107BA), (0x1DF00, 0x1DF1E),
]
_STARTS = [a for a, _ in RANGES]

_MAP = {"【": "[", "】": "]", "〔": "[", "〕": "]", "〖": "[", "〗": "]", "「": "\"", "」": "\"",
        "『": "\"", "』": "\"", "《": "«", "》": "»", "〈": "<", "〉": ">", "、": ",", "。": ".",
        "・": "·", "\u3000": " "}
_SPACES = re.compile(r"[ \t]{2,}")
_BRACKET_GAP = re.compile(r"(?<=\[) | (?=\])")


def covered(ch):
    o = ord(ch)
    i = bisect.bisect_right(_STARTS, o) - 1
    return i >= 0 and RANGES[i][0] <= o <= RANGES[i][1]


def _fix(ch):
    if ch in _MAP:
        return _MAP[ch]
    if ch in "\u200d\ufe0e\ufe0f":               # emoji joiner / emoji presentation selectors
        return ""
    o = ord(ch)
    if 0xFF01 <= o <= 0xFF5E:                      # full-width ASCII forms
        return chr(o - 0xFEE0)
    if covered(ch) or ch in "\t\n":
        return ch
    if unicodedata.category(ch)[0] == "L":         # letters (e.g. Chinese) are kept even if not drawable
        return ch
    if unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return ""                                  # variation selectors, joiners
    return " "                                     # emoji / symbols: keep the word gap


def clean_label(text):
    if not text:
        return text
    out = _SPACES.sub(" ", "".join(_fix(c) for c in str(text))).strip()
    out = _BRACKET_GAP.sub("", out)
    return out or str(text).strip()
