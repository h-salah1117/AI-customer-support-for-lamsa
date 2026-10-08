from app.data.product_repository import ProductRepository

def test_find_by_sku():
    repo = ProductRepository()
    repo.load_products()

    product = repo.find_by_sku("LMS-001-XL")

    assert product is not None
    assert product.sku == "LMS-001-XL"

    assert repo.find_by_sku("NOT-EXIST") is None