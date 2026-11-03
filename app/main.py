from app.data.product_repository import ProductRepository
from app.services.product_service import ProductService
from dataclasses import dataclass


def build_service(ripo: ProductRepository = None) -> "Services":
    if ripo is None:
        ripo = ProductRepository()
    ripo.load_products()
    service = ProductService(ripo)
    return Services(product=service, order=None)  # Placeholder for OrderService, to be implemented later
@dataclass
class Services:
    product: ProductService
    order: None  # Placeholder for OrderService, to be implemented later


if __name__ == "__main__":
    build_service()


    
