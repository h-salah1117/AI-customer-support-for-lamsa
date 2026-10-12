"""
Responsibilities:

Check product availability
Determine available alternatives (sizes/colors)
Update/reduce stock after confirmed order
"""

# ProductService

#     __init__
#         ↓
#     receive ProductRepository

from app.data.product_repository import Product


class ProductService:
    def __init__(self, repository):
        self.product_repository = repository
        print("Service created")

    #     get_product(sku)
    #         ↓
    #     repository.find_by_sku(sku)
    def get_product(self, sku) -> Product | None:
        return self.product_repository.find_by_sku(sku)

    #     check_availability(sku, quantity)
    #         ↓
    #     get product
    #         ↓
    #     does product exist?
    #         ↓
    #     is stock >= quantity?
    #         ↓
    #     available / unavailable

    def check_availability(self, sku, quantity) -> bool:
        product = self.get_product(sku)
        if not product or quantity <= 0:
            return False
        return product.stock_qty >= quantity

    #     reduce_stock(sku, quantity)
    #         ↓
    #     get product
    #         ↓
    #     does product exist?
    #         ↓
    #     is stock >= quantity?
    #         ↓
    #     decrease stock
    #         ↓
    #     return result
    def reduce_stock(self, sku, quantity) -> bool:
        product = self.get_product(sku)
        if not product or quantity <= 0:
            return False
        if product.stock_qty < quantity:
            return False
        product.stock_qty -= quantity
        return True

    def get_all_products(self) -> list[Product]:
        return self.product_repository.get_all_products()

    def get_size_alternatives(self, sku, quantity) -> list[Product]:
        product = self.get_product(sku)
        if not product or quantity <= 0:
            return []
        alternatives = []
        for p in self.get_all_products():
            if (
                p.name == product.name
                and p.color == product.color
                and p.size != product.size
                and self.check_availability(p.sku, quantity)
            ):
                alternatives.append(p)
        return alternatives

    def get_color_alternatives(self, sku, quantity) -> list[Product]:
        product = self.get_product(sku)
        if not product or quantity <= 0:
            return []
        alternatives = []
        for p in self.get_all_products():
            if (
                p.name == product.name
                and p.size == product.size
                and p.color != product.color
                and self.check_availability(p.sku, quantity)
            ):
                alternatives.append(p)
        return alternatives
