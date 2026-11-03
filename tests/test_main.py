from app.main import build_service
from app.data.product_repository import Product
from app.services.product_service import ProductService
import pytest
from tests.test_product_service import PRODUCTS
from app.data.product_repository import ProductRepository



def test_build_services():
    services = build_service()  
    assert isinstance(services.product, ProductService)
    assert services.order is None
    assert services.product.get_product('LMS-001-M') is not None  # Ensure the product service is initialized correctly