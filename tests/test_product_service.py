import pytest
from app.data.product_repository import Product
from app.services.product_service import ProductService


class FakeProductRepository:
    def __init__(self, products):
        self.products = {p.sku: p for p in products}

    def find_by_sku(self, sku):
        return self.products.get(sku)

    def get_all_products(self):
        return list(self.products.values())


def make_product(sku, name, color, size, stock_qty):
    return Product(
        sku=sku,
        name=name,
        category="test",
        color=color,
        size=size,
        price=100,
        stock_qty=stock_qty,
        delivery_time="3-5 أيام",
    )


# Every product is here for a reason (see the comment next to it)
PRODUCTS = [
    # Hoodie, navy: M is the original, L is out of stock, XL is the valid size alternative
    make_product("HOOD-NAVY-M", "هودي", "كحلي", "M", stock_qty=9),
    make_product("HOOD-NAVY-L", "هودي", "كحلي", "L", stock_qty=0),
    make_product("HOOD-NAVY-XL", "هودي", "كحلي", "XL", stock_qty=9),
    # T-shirt in size M: white is the original, black is the valid color alternative, beige is out of stock
    make_product("TEE-WHITE-M", "تيشرت", "ابيض", "M", stock_qty=15),
    make_product("TEE-BLACK-M", "تيشرت", "اسود", "M", stock_qty=5),
    make_product("TEE-BEIGE-M", "تيشرت", "بيج", "M", stock_qty=0),
    # Different product, same color and size as TEE-BLACK-M: must never show up as an alternative
    make_product("PANTS-BLACK-M", "بنطلون", "اسود", "M", stock_qty=8),
]


@pytest.fixture
def service():
    # model_copy() gives every test its own products, so reduce_stock in one test
    # can't change the stock another test sees
    repo = FakeProductRepository([p.model_copy() for p in PRODUCTS])
    return ProductService(repo)


def skus(products):
    return sorted(p.sku for p in products)


# ---------- get_product ----------


def test_get_product_existing(service):
    assert service.get_product("TEE-WHITE-M").name == "تيشرت"


def test_get_product_unknown_sku_returns_none(service):
    assert service.get_product("NOT-EXIST") is None


# ---------- get_all_products ----------


def test_get_all_products_returns_every_product(service):
    assert skus(service.get_all_products()) == skus(PRODUCTS)


# ---------- check_availability ----------


@pytest.mark.parametrize(
    "sku, quantity",
    [
        pytest.param("TEE-WHITE-M", 1, id="one"),
        pytest.param("TEE-WHITE-M", 15, id="exactly_all_stock"),
    ],
)
def test_check_availability_true(service, sku, quantity):
    assert service.check_availability(sku, quantity) is True


@pytest.mark.parametrize(
    "sku, quantity",
    [
        pytest.param("TEE-WHITE-M", 16, id="one_more_than_stock"),
        pytest.param("HOOD-NAVY-L", 1, id="out_of_stock"),
        pytest.param("TEE-WHITE-M", 0, id="zero_quantity"),
        pytest.param("TEE-WHITE-M", -3, id="negative_quantity"),
        pytest.param("NOT-EXIST", 1, id="unknown_sku"),
    ],
)
def test_check_availability_false(service, sku, quantity):
    assert service.check_availability(sku, quantity) is False


# ---------- reduce_stock ----------


def test_reduce_stock_success_decreases_stock(service):
    assert service.reduce_stock("TEE-WHITE-M", 5) is True
    assert service.get_product("TEE-WHITE-M").stock_qty == 10


def test_reduce_stock_exactly_all_stock_leaves_zero(service):
    assert service.reduce_stock("TEE-WHITE-M", 15) is True
    assert service.get_product("TEE-WHITE-M").stock_qty == 0


@pytest.mark.parametrize(
    "quantity",
    [
        pytest.param(16, id="more_than_stock"),
        pytest.param(0, id="zero"),
        pytest.param(-5, id="negative"),
    ],
)
def test_reduce_stock_rejected_leaves_stock_unchanged(service, quantity):
    assert service.reduce_stock("TEE-WHITE-M", quantity) is False
    assert service.get_product("TEE-WHITE-M").stock_qty == 15


def test_reduce_stock_unknown_sku(service):
    assert service.reduce_stock("NOT-EXIST", 1) is False


def test_tests_are_isolated_from_each_other(service):
    # Runs after the reduce_stock tests: if the fixture shared products, this would be 10 or 0
    assert service.get_product("TEE-WHITE-M").stock_qty == 15


# ---------- get_size_alternatives ----------


def test_size_alternatives_returns_only_in_stock_other_sizes(service):
    # L is out of stock, M is the original -> only XL
    assert skus(service.get_size_alternatives("HOOD-NAVY-M", 1)) == ["HOOD-NAVY-XL"]


def test_size_alternatives_respects_requested_quantity(service):
    # XL has 9, so asking for 10 leaves nothing
    assert service.get_size_alternatives("HOOD-NAVY-M", 10) == []


@pytest.mark.parametrize(
    "sku, quantity",
    [
        pytest.param("NOT-EXIST", 1, id="unknown_sku"),
        pytest.param("HOOD-NAVY-M", 0, id="zero_quantity"),
    ],
)
def test_size_alternatives_invalid_input_returns_empty(service, sku, quantity):
    assert service.get_size_alternatives(sku, quantity) == []


# ---------- get_color_alternatives ----------


def test_color_alternatives_returns_only_same_product_in_stock(service):
    # Beige is out of stock, pants are a different product -> only black t-shirt
    assert skus(service.get_color_alternatives("TEE-WHITE-M", 1)) == ["TEE-BLACK-M"]


def test_color_alternatives_respects_requested_quantity(service):
    # Black has 5, so asking for 6 leaves nothing
    assert service.get_color_alternatives("TEE-WHITE-M", 6) == []


@pytest.mark.parametrize(
    "sku, quantity",
    [
        pytest.param("NOT-EXIST", 1, id="unknown_sku"),
        pytest.param("TEE-WHITE-M", -1, id="negative_quantity"),
    ],
)
def test_color_alternatives_invalid_input_returns_empty(service, sku, quantity):
    assert service.get_color_alternatives(sku, quantity) == []
