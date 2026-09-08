"""Entidad Caja Registradora del automercado."""

from typing import Optional, Tuple, List
from src.constants import CheckoutState
from src.models.customer import Customer


class CheckoutCounter:
    """Representa una caja registradora con cinta transportadora, escaner y cajero."""

    def __init__(
        self,
        counter_id: int,
        position: Tuple[int, int],
        is_express: bool = False,
        is_active: bool = True,
    ):
        self.id = counter_id
        self.x, self.y = position
        self.is_express = is_express
        self.is_active = is_active
        self.state = CheckoutState.OPEN if is_active else CheckoutState.CLOSED

        self.current_customer: Optional[Customer] = None
        self.scanner_active = False
        self.items_on_belt: List[Tuple[int, int, int]] = []

        # Contadores de rendimiento operativo
        self.customers_served_count = 0
        self.items_scanned_count = 0
        self.total_busy_time = 0.0

    @property
    def is_free(self) -> bool:
        """Indica si la caja esta abierta y lista para recibir un cliente."""
        return self.is_active and self.state == CheckoutState.OPEN and self.current_customer is None

    def assign_customer(self, customer: Customer):
        """Asigna un cliente a la estacion de cobro."""
        self.current_customer = customer
        customer.assigned_checkout_id = self.id
        self.state = CheckoutState.BUSY
        self.scanner_active = True
        self.items_on_belt = list(customer.item_colors[:8])

    def release_customer(self) -> Optional[Customer]:
        """Libera la estacion tras culminar el cobro."""
        cust = self.current_customer
        if cust:
            self.customers_served_count += 1
            self.items_scanned_count += cust.num_items

        self.current_customer = None
        self.scanner_active = False
        self.items_on_belt.clear()
        self.state = CheckoutState.OPEN if self.is_active else CheckoutState.CLOSED
        return cust

    def open_counter(self):
        """Abre la caja registradora para atencion al publico."""
        self.is_active = True
        if self.current_customer is None:
            self.state = CheckoutState.OPEN

    def close_counter(self):
        """Cierra la caja registradora tras terminar la atencion en curso."""
        self.is_active = False
        if self.current_customer is None:
            self.state = CheckoutState.CLOSED
