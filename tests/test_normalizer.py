import pytest
from app.utils.normalizer import Normalizer

normalizer = Normalizer()

@pytest.mark.parametrize("input_text, expected",  [
    pytest.param("عايز اللون الأسود", "عايز اللون الاسود",id="hamza"),
    pytest.param("عايز أسأل علي البرتقالى", "عايز اسال علي البرتقالي",id="hamza and yaa"),
    pytest.param("بكام الجزمة ", "بكام الجزمه",id="taa marbouta"),
    pytest.param("عايز     أشتري    تيشيرت", "عايز اشتري تيشيرت",id="extra spaces"),
    pytest.param("عايز-أشتري-تيشيرت", "عايز اشتري تيشيرت",id="hyphen"),
    pytest.param("جزْمة", "جزمه", id="sukun"),
    pytest.param("جـــزمة", "جزمه", id="tatweel"),
    pytest.param("جـزْمـة", "جزمه", id="sukun_and_tatweel"),
    pytest.param("عايز   جـــزْمة", "عايز جزمه", id="tatweel_sukun_extra_spaces"),
])
def test_normalize_text(input_text, expected):
    assert normalizer.normalize_text(input_text) == expected


def test_normalize_text_rejects_non_string():
    with pytest.raises(ValueError):
        normalizer.normalize_text(2837734)