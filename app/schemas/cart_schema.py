from pydantic import BaseModel

# Owner: Person B (cart) — agree on these shapes as a team first (checkout and frontend depend on them).

# TODO: does a cart need a status? What happens to a cart after checkout — deleted, cleared, or closed?
#       (Hint: re-read "Checkout & orders" and "Historical integrity" in the spec.)


############################################################################################
### Requests
############################################################################################

class CartItemAdd(BaseModel):
    # TODO: what identifies a menu item uniquely? Look at how generate_menu_item_id builds IDs.
    # TODO: what are valid quantities, and where is that rule enforced (schema, service, or both)?
    pass


class CartItemUpdate(BaseModel):
    # TODO: what can be changed about an item that is already in the cart?
    pass


############################################################################################
### Responses
############################################################################################

class CartItem(BaseModel):
    # TODO: what does the frontend need to display one cart line?
    pass


class CartResponse(BaseModel):
    """A customer's cart as returned by the API."""
    # TODO: which values must be calculated by the backend rather than sent by the client?
    # TODO: how does the cart remember which restaurant it belongs to? What if it is empty?
    pass
