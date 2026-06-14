from app.utils.slug import slugify


def test_basic_slugify():
    assert slugify("Hello World") == "hello-world"


def test_accented_chars():
    assert slugify("Barranquilla") == "barranquilla"
    assert slugify("Rincón del Mar") == "rincon-del-mar"


def test_special_chars_removed():
    assert slugify("Castillo de San Felipe!") == "castillo-de-san-felipe"


def test_multiple_spaces():
    assert slugify("Gran  Malecón") == "gran-malecon"


def test_leading_trailing_hyphens():
    assert slugify("-hello-") == "hello"
