"""
 Responsibilities:

Maintain conversation context
Store selected product/specs
Keep different products/items separated
Maintain context across multiple messages
Track the current conversation state


Conversation Session :
├── customer_id
├── current product/item context
│   ├── product
│   ├── color
│   ├── size
│   └── quantity
└── conversation_state
"""

from enum import Enum
from pydantic import BaseModel, Field


# Define conversation state lifecycle
class ConversationState(str, Enum):
    IDLE = "idle"
    BROWSING_CATALOG = "browsing_catalog"
    SELECTING_SPECS = "selecting_specs"
    BUILDING_ORDER = "building_order"
    AWAITING_CONFIRMATION = "awaiting_confirmation"


# Item context extracted from user natural language
class ItemContext(BaseModel):
    product_name: str | None = None
    category: str | None = None
    color: str | None = None
    size: str | None = None
    quantity: int = 1
    selected_sku: str | None = None


# Session model tracking user context across turns
class ConversationSession(BaseModel):
    customer_id: str
    current_item: ItemContext = Field(default_factory=ItemContext)
    conversation_state: ConversationState = ConversationState.IDLE
    recent_history: list[dict[str, str]] = Field(default_factory=list)


class ConversationService:
    def __init__(self):
        # In-memory store for user active sessions mapped by phone number
        self._sessions: dict[str, ConversationSession] = {}

    def get_or_create_session(self, customer_id: str) -> ConversationSession:
        # Retrieve existing session or spawn new session for customer
        if customer_id not in self._sessions:
            self._sessions[customer_id] = ConversationSession(customer_id=customer_id)
        return self._sessions[customer_id]

    def update_item_context(
        self, customer_id: str, new_specs: dict
    ) -> ConversationSession:
        # Merge updated specs into existing item context without overwriting previous selections
        session = self.get_or_create_session(customer_id)

        for key, value in new_specs.items():
            if value is not None and hasattr(session.current_item, key):
                setattr(session.current_item, key, value)

        return session

    def reset_item_context(self, customer_id: str) -> ConversationSession:
        # Clear item context once item is committed to cart or cancelled
        session = self.get_or_create_session(customer_id)
        session.current_item = ItemContext()
        return session

    def transition_state(
        self, customer_id: str, new_state: ConversationState
    ) -> ConversationSession:
        # Transition session to new lifecycle state
        session = self.get_or_create_session(customer_id)
        session.conversation_state = new_state
        return session
