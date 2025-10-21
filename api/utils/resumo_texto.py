import re
import unicodedata

URL_RE   = re.compile(r'https?://\S+|www\.\S+')
EMAIL_RE = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')
PHONE_RE = re.compile(r'(?:(?:\+?\d{1,3}\s*)?(?:\(?\d{2,3}\)?\s*)?\d[\d\s\-.()]{6,}\d)')

# Fallback simples para emojis (cobre as faixas mais comuns)
EMOJI_RE = re.compile(
    '['
    '\U0001F600-\U0001F64F'  # emoticons
    '\U0001F300-\U0001F5FF'  # símbolos/pictogramas
    '\U0001F680-\U0001F6FF'  # transporte/mapa
    '\U0001F1E0-\U0001F1FF'  # bandeiras
    '\U00002600-\U000026FF'  # símbolos diversos
    '\U00002700-\U000027BF'  # dingbats
    ']+', flags=re.UNICODE
)

CONTROL_RE = re.compile(r'[\u0000-\u0008\u000B-\u000C\u000E-\u001F\u007F]')

def _strip_or_demojize(text: str, demojize: bool) -> str:
    """
    Se 'emoji' estiver instalado, usa-o; senão aplica o fallback (remove).
    'demojize=True' transforma 😀 -> :grinning_face: (útil se o emoji carrega contexto).
    """
    if demojize:
        try:
            import emoji
            # Observação: demojize costuma retornar nomes em inglês (:smiling_face:).
            return emoji.demojize(text)
        except Exception:
            # Sem lib 'emoji', apenas removemos
            return EMOJI_RE.sub('', text)
    else:
        try:
            import emoji
            return emoji.replace_emoji(text, replace='')
        except Exception:
            return EMOJI_RE.sub('', text)

def comprimir(
    text: str,
    *,
    keep_placeholders: bool = True,
    demojize_emojis: bool = False,
    lowercase: bool = False,
    max_chars: int | None = None
) -> str:
    """
    Limpa e compacta texto para envio à LLM, preservando contexto essencial.
    """
    if not text:
        return ''

    # 1) Normalização Unicode
    s = unicodedata.normalize('NFKC', text)

    # 2) Emojis: remover ou demojizar
    s = _strip_or_demojize(s, demojize=demojize_emojis)

    # 3) Placeholders de entidades que "poluem" tokens mas mantêm contexto
    if keep_placeholders:
        s = URL_RE.sub('<URL>', s)
        s = EMAIL_RE.sub('<EMAIL>', s)
        s = PHONE_RE.sub('<PHONE>', s)
    else:
        s = URL_RE.sub('', s)
        s = EMAIL_RE.sub('', s)
        s = PHONE_RE.sub('', s)

    # 4) Remove caracteres de controle (exceto espaço e pontuação comuns)
    s = CONTROL_RE.sub('', s)

    # 5) Reduz repetições exageradas
    s = re.sub(r'([!?.,;:])\1{1,}', r'\1', s)   # "!!!??" -> "!?"
    s = re.sub(r'(.)\1{2,}', r'\1\1', s)        # "soooo" -> "soo"

    # 6) Espaços e quebras
    s = re.sub(r'\s+', ' ', s).strip()

    # 7) Lowercase (opcional)
    if lowercase:
        s = s.lower()

    # 8) Limite final (char-based; bom o bastante p/ reduzir tokens)
    if max_chars and len(s) > max_chars:
        s = s[: max(0, max_chars - 1)] + '…'

    return s
