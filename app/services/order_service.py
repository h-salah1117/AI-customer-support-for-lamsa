'''
    Responsibilities:

Manage order confirmation
Re-check required availability before confirmation
Coordinate stock reduction through product_service
Create/update order status
Notify seller
Handle notification retry/failure
Return confirmation result so the response layer tells the customer
'''

from enum import Enum
from pydantic import BaseModel, Field, NonNegativeInt, PositiveFloat
from app.models.product import Product
from app.services.product_service import ProductService
from app.utils.whatsapp_client import WhatsAppClient


# Enum defining order lifecycle statuses
class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


# Model representing a single cart line item
class OrderItem(BaseModel):
    sku: str
    product_name: str
    color: str
    size: str
    unit_price: PositiveFloat
    quantity: NonNegativeInt = Field(default=1)


# Model representing the full customer order
class Order(BaseModel):
    customer_id: str
    items: list[OrderItem] = Field(default_factory=list)
    status: OrderStatus = OrderStatus.DRAFT
    delivery_address: str | None = None

    @property
    def total_price(self) -> float:
        # Calculate total price for all items in order
        return sum(item.unit_price * item.quantity for item in self.items)


# Result model returned to the response/orchestrator layer
class OrderConfirmationResult(BaseModel):
    success: bool
    order_id: str | None = None
    message: str
    failed_skus: list[str] = Field(default_factory=list)


class OrderService:
    def __init__(
        self,
        product_service: ProductService,
        whatsapp_client: WhatsAppClient,
        seller_phone: str,
    ):
        self.product_service = product_service
        self.whatsapp_client = whatsapp_client
        self.seller_phone = seller_phone
        # In-memory store for active orders mapped by customer_id
        self._orders: dict[str, Order] = {}

    def get_or_create_draft_order(self, customer_id: str) -> Order:
        # Fetch existing active draft order or initialize new one
        if (
            customer_id not in self._orders
            or self._orders[customer_id].status != OrderStatus.DRAFT
        ):
            self._orders[customer_id] = Order(customer_id=customer_id)
        return self._orders[customer_id]

    def add_item_to_cart(
        self, customer_id: str, product: Product, quantity: int = 1
    ) -> tuple[bool, str]:
        # Step 1: Validate stock availability before adding
        if not self.product_service.check_availability(product.sku, quantity):
            return False, f"Requested quantity for SKU {product.sku} is not available in stock."

        order = self.get_or_create_draft_order(customer_id)

        # Step 2: Merge quantity if SKU already exists in active cart
        for item in order.items:
            if item.sku == product.sku:
                new_qty = item.quantity + quantity
                if not self.product_service.check_availability(product.sku, new_qty):
                    return False, f"Cannot add {quantity} more. Stock limit reached."
                item.quantity = new_qty
                return True, "Item quantity updated in cart."

        # Step 3: Append new OrderItem if SKU is not in cart
        new_item = OrderItem(
            sku=product.sku,
            product_name=product.name,
            color=product.color,
            size=product.size,
            unit_price=product.price,
            quantity=quantity,
        )
        order.items.append(new_item)
        return True, "Item successfully added to cart."

    def _notify_seller(self, order: Order) -> bool:
        # Prepare structured order details payload for WhatsApp API dispatch
        order_details = {
            "customer_id": order.customer_id,
            "delivery_address": order.delivery_address,
            "total_price": order.total_price,
            "items": [
                {
                    "product_name": item.product_name,
                    "color": item.color,
                    "size": item.size,
                    "quantity": item.quantity,
                }
                for item in order.items
            ],
        }

        # Dispatch alert using external WhatsApp client with built-in retries
        return self.whatsapp_client.send_seller_notification(
            seller_phone=self.seller_phone, order_details=order_details
        )

    def confirm_order(
        self, customer_id: str, delivery_address: str
    ) -> OrderConfirmationResult:
        order = self._orders.get(customer_id)

        # Step 1: Validate cart state
        if not order or not order.items or order.status != OrderStatus.DRAFT:
            return OrderConfirmationResult(
                success=False,
                message="No active draft cart found to confirm.",
            )

        # Step 2: Re-check required availability before final confirmation
        failed_skus = []
        for item in order.items:
            if not self.product_service.check_availability(item.sku, item.quantity):
                failed_skus.append(item.sku)

        if failed_skus:
            return OrderConfirmationResult(
                success=False,
                message="Some items in your cart are no longer available in requested quantities.",
                failed_skus=failed_skus,
            )

        # Step 3: Coordinate stock reduction through product_service
        for item in order.items:
            self.product_service.reduce_stock(item.sku, item.quantity)

        # Step 4: Update order status & delivery details
        order.delivery_address = delivery_address
        order.status = OrderStatus.CONFIRMED

        # Step 5: Trigger seller notification via WhatsApp Client
        notification_sent = self._notify_seller(order)

        # Step 6: Return structured result
        return OrderConfirmationResult(
            success=True,
            order_id=f"ORD-{customer_id[-4:]}",
            message="Order confirmed successfully!",
        )