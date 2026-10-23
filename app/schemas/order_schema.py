from enum import Enum

from pydantic import BaseModel

# Owner: Person C (checkout + orders) — agree on these shapes as a team first.


class OrderStatus(str, Enum):
    """States an order can be in."""
    # TODO: which state does a newly created order start in?
    # TODO: M3 needs the full lifecycle — sketch it now so the stored data won't need migrating later.
    pass


class OrderItem(BaseModel):
    """One line of an order."""
    # TODO: if a restaurant changes a price next week, should this order change? What must be copied vs referenced?
    pass


class OrderResponse(BaseModel):
    # TODO: what information "represents the transaction" (spec wording)?
    # TODO: which customer/restaurant details must be a snapshot taken at checkout time?
    pass
