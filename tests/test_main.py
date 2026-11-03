from app.main import build_service
from app.data.product_repository import Product
from app.services.product_service import ProductService
import pytest


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


def test_build_services():
    services = build_service()  
    assert isinstance(services.get_product, ProductService)
    assert services.order is None