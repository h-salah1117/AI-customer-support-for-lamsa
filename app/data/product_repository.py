'''
Product
├── sku: string
├── name: string
├── category: string
├── color: string
├── size: string
├── price: positive number
├── stock_qty: non-negative integer
└── delivery_time: string
'''


# CSV
#  ↓
# load_products()
#  ├── parse
#  ├── validate Product
#  ├── validate SKU uniqueness
#  └── build products_by_sku
#           ↓
#        dict[str, Product]


import pandas as pd
from pydantic import BaseModel, NonNegativeInt, PositiveFloat , Field
from app.config import config
from app.utils.normalizer import Normalizer

normalizer = Normalizer()

class Product(BaseModel):
    sku: str = Field(min_length=3)
    name: str
    category: str
    color: str
    size: str
    price: PositiveFloat
    stock_qty: NonNegativeInt
    delivery_time: str = Field(min_length=1)

class ProductRepository:
    def __init__(self):
        self.product_by_sku = {}
    

    def load_products(self):
# Read raw data from CSV
        raw_data = pd.read_csv(config["data"]["products_path"])
        raw_data["name"] = raw_data["name"].apply(normalizer.normalize_text)
        raw_data["color"] = raw_data["color"].apply(normalizer.normalize_text)
        raw_data["size"] = raw_data["size"].apply(normalizer.normalize_text)
# Iterate over records and validate each row using Pydantic
        for row in raw_data.to_dict(orient="records"):       
            product = Product(**row)  
# check for duplicate SKUs and raise an error if found 
            if product.sku in self.product_by_sku:
                    raise ValueError(f"Duplicate SKU found: {product.sku}")
            else:
                    self.product_by_sku[product.sku] = product

    def find_by_sku(self, sku: str) -> Product | None:
        return self.product_by_sku.get(sku)
    
    def get_all_products(self) -> list[Product]:
        return list(self.product_by_sku.values())
