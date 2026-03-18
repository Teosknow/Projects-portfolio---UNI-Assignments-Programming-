from datetime import date
from typing import List, Optional


# =====================================================
# Installment Class
# =====================================================
class Installment:
    """
    Represents a single installment in a student's payment plan.
    """

    def __init__(self, amount: float, due_date: date) -> None:
        # Amount of money due for this installment
        self.amount: float = amount

        # Due date for the payment
        self.due_date: date = due_date

        # Flag indicating whether the installment has been paid
        self.paid: bool = False

        # Date when the installment was paid (None if unpaid)
        self.paid_date: date | None = None

    def mark_paid(self) -> None:
        """
        Mark this installment as paid.
        """
        # Set payment status to paid
        self.paid = True

        # Store payment date only the first time it is paid
        if self.paid_date is None:
            self.paid_date = date.today()

    # -------------------------
    # Convenience properties
    # -------------------------
    @property
    def status(self) -> str:
        """
        Return a human-readable status string.
        """
        return "PAID" if self.paid else "DUE"

    @property
    def is_overdue(self) -> bool:
        """
        Check if the installment is overdue.
        """
        # Overdue if unpaid AND due date has passed
        return (not self.paid) and (self.due_date < date.today())


# =====================================================
# PaymentPlan Class
# =====================================================
class PaymentPlan:
    """
    Represents a payment plan for a student.
    """

    # Base fees
    YEARLY_FEE: float = 400.0
    TRIMESTRAL_TOTAL: float = 440.0

    # Allowed payment plan types
    PAYMENT_YEARLY = "yearly"
    PAYMENT_TRIMESTRAL = "trimestral"

    def __init__(self, payment_type: str, courses_count: int) -> None:
        # Validate number of courses
        if courses_count <= 0:
            raise ValueError("courses_count must be positive")

        # Normalize and validate payment type
        payment_type = payment_type.lower()
        if payment_type not in {self.PAYMENT_YEARLY, self.PAYMENT_TRIMESTRAL}:
            raise ValueError("Invalid payment type")

        # Store plan configuration
        self.payment_type: str = payment_type
        self.courses_count: int = courses_count

        # Compute discount based on number of courses
        self.discount: float = self._calculate_discount()

        # List of generated installments
        self.installments: List[Installment] = []

        # Automatically create installments at initialization
        self._create_installments()

    # -------------------------
    # Internal helpers
    # -------------------------
    def _calculate_discount(self) -> float:
        """
        Calculate discount based on number of courses.
        """
        if self.courses_count == 2:
            return 0.05
        if self.courses_count >= 3:
            return 0.10
        return 0.0

    def _create_installments(self) -> None:
        """
        Generate installments based on payment plan type.
        """
        # Remove any existing installments before regenerating
        self.installments.clear()

        # Use current year for due dates
        year = date.today().year

        # Yearly payment → one single installment
        if self.payment_type == self.PAYMENT_YEARLY:
            total = self.YEARLY_FEE * self.courses_count * (1 - self.discount)
            self.installments.append(Installment(total, date(year, 11, 10)))

        # Trimestral payment → three installments
        elif self.payment_type == self.PAYMENT_TRIMESTRAL:
            total = self.TRIMESTRAL_TOTAL * self.courses_count * (1 - self.discount)

            # Split total into three parts, fixing rounding on the last one
            base_amount = round(total / 3, 2)
            amounts = [
                base_amount,
                base_amount,
                round(total - 2 * base_amount, 2),
            ]

            # Due months: September, January, May
            months = [9, 1, 5]

            # Create each installment
            for amount, month in zip(amounts, months):
                self.installments.append(Installment(amount, date(year, month, 10)))

    # -------------------------
    # Business logic
    # -------------------------
    def has_payments(self) -> bool:
        """
        Check if at least one installment has been paid.
        """
        return any(inst.paid for inst in self.installments)

    def update_for_courses(self, courses_count: int) -> None:
        """
        Update the payment plan if the number of courses changes.
        """
        # Validate new course count
        if courses_count <= 0:
            raise ValueError("courses_count must be positive")

        # Prevent changes after payments started
        if self.has_payments():
            raise RuntimeError("Cannot modify payment plan after payments have started")

        # Update plan only if the value actually changed
        if courses_count != self.courses_count:
            self.courses_count = courses_count
            self.discount = self._calculate_discount()
            self._create_installments()

    def mark_installment_paid(self, index: int) -> None:
        """
        Mark an installment as paid by index.
        """
        if not 0 <= index < len(self.installments):
            raise IndexError("Invalid installment index")

        self.installments[index].mark_paid()

    # -------------------------
    # Convenience properties
    # -------------------------
    @property
    def installment_count(self) -> int:
        """Return number of installments."""
        return len(self.installments)

    @property
    def total_amount(self) -> float:
        """Total amount of the payment plan."""
        return sum(inst.amount for inst in self.installments)

    @property
    def paid_amount(self) -> float:
        """Total amount already paid."""
        return sum(inst.amount for inst in self.installments if inst.paid)

    @property
    def unpaid_amount(self) -> float:
        """Remaining amount to be paid."""
        return self.total_amount - self.paid_amount

    @property
    def next_due_installment(self) -> Optional[Installment]:
        """
        Return the next unpaid installment, if any.
        """
        for inst in self.installments:
            if not inst.paid:
                return inst
        return None

    @property
    def next_due_date(self) -> Optional[date]:
        """
        Return the due date of the next unpaid installment.
        """
        nxt = self.next_due_installment
        return nxt.due_date if nxt else None

    @property
    def is_yearly(self) -> bool:
        """True if the plan is yearly."""
        return self.payment_type == self.PAYMENT_YEARLY

    @property
    def is_trimestral(self) -> bool:
        """True if the plan is trimestral."""
        return self.payment_type == self.PAYMENT_TRIMESTRAL
