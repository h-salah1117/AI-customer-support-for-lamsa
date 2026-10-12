
class Normalizer:
    # حركات + تطويلة: تتشال خالص
    DIACRITICS = "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0640"
    PUNCTUATION = "!@#$%^&*()_=+[]{};:'\",<>./?\\|-"

    def __init__(self):
        self._remove_table = str.maketrans("", "", self.DIACRITICS)
        self._punct_table = str.maketrans({c: " " for c in self.PUNCTUATION})
        self._letter_table = str.maketrans({
            "أ": "ا", "إ": "ا", "آ": "ا",
            "ى": "ي",
            "ة": "ه",
        })

    def normalize_text(self, text):
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")

        text = text.lower()
        text = text.translate(self._remove_table)   # شيل الحركات والتطويلة
        text = text.translate(self._punct_table)    # الترقيم لمسافة
        text = text.translate(self._letter_table)   # توحيد الحروف
        return " ".join(text.split())               # مسافات زيادة + strip