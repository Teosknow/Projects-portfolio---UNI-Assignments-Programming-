from typing import Optional, Callable, Dict
from datetime import date
from student import Student


# =====================================================
# Custom exception
# =====================================================
class InvalidEmailError(Exception):
    """
    Raised when an email fails validation checks.
    """

    pass


# =====================================================
# Email validation helper
# =====================================================
def validate_email(email: str) -> bool:
    """
    Validate an email string using basic structural rules.
    Raises InvalidEmailError if invalid.
    """

    # Must contain exactly one '@'
    if email.count("@") != 1:
        raise InvalidEmailError("Invalid email: must contain exactly one '@'")

    # Split local and domain parts
    local, domain = email.split("@")

    # Local part must exist
    if not local:
        raise InvalidEmailError("Invalid email: missing local part before '@'")

    # No spaces allowed anywhere
    if " " in email:
        raise InvalidEmailError("Invalid email: spaces are not allowed")

    # ---- Local part checks ----
    if local.startswith(".") or local.endswith("."):
        raise InvalidEmailError(
            "Invalid email: local part cannot start or end with '.'"
        )

    if ".." in local:
        raise InvalidEmailError(
            "Invalid email: local part cannot contain consecutive dots"
        )

    # ---- Domain checks ----
    if domain.startswith(".") or domain.endswith("."):
        raise InvalidEmailError("Invalid email: domain cannot start or end with '.'")

    if ".." in domain:
        raise InvalidEmailError("Invalid email: domain cannot contain consecutive dots")

    # Domain must contain at least one dot
    if "." not in domain:
        raise InvalidEmailError("Invalid email: domain must contain at least one '.'")

    # Split domain into labels and ensure none are empty
    labels = domain.split(".")
    if any(not label for label in labels):
        raise InvalidEmailError("Invalid email: empty domain label")

    # Top-level domain must be at least 2 characters
    tld = labels[-1]
    if len(tld) < 2:
        raise InvalidEmailError("Invalid email: domain ending too short")

    return True


# =====================================================
# Generic input helper
# =====================================================
def get_input(
    prompt: str, validator: Optional[Callable[[str], bool]] = None
) -> Optional[str]:
    """
    Read user input from console with optional validation.
    """

    while True:
        # Read and normalize input
        val = input(f"{prompt}: ").strip()

        # 'b' means go back / cancel
        if val.lower() == "b":
            return None

        # Apply validator if provided
        if validator:
            try:
                ok = validator(val)
            except Exception as e:
                # Validator raised an error → show message and retry
                print(e)
                continue

            # Validator returned False
            if not ok:
                print("Invalid input.")
                continue

        return val


# =====================================================
# Date input helper
# =====================================================
def get_date_input(prefix: str = "Birth") -> Optional[date]:
    """
    Prompt user for a valid date (YYYY-MM-DD via separate inputs).
    """

    current_year = date.today().year

    while True:
        # Read year
        year_input = input(f"{prefix} year (YYYY): ").strip()
        if year_input.lower() == "b":
            return None

        # Read month
        month_input = input(f"{prefix} month (1-12): ").strip()
        if month_input.lower() == "b":
            return None

        # Read day
        day_input = input(f"{prefix} day (1-31): ").strip()
        if day_input.lower() == "b":
            return None

        try:
            # Convert to integers
            year, month, day = int(year_input), int(month_input), int(day_input)

            # Year validation
            if len(year_input) != 4 or not (1930 <= year <= current_year):
                raise ValueError(f"Year must be between 1930 and {current_year}.")

            # Month/day validation
            if not (1 <= month <= 12) or not (1 <= day <= 31):
                raise ValueError("Month or day out of range.")

            return date(year, month, day)

        except ValueError as e:
            print(f"Insert valid date format: {e}")


# =====================================================
# Specialized email input
# =====================================================
def get_email_input() -> Optional[str]:
    """
    Prompt for an email address and validate it.
    """

    while True:
        mail = get_input("Email")

        # User chose to go back
        if mail is None:
            return None

        try:
            # Validate and normalize email
            if validate_email(mail):
                return mail.lower()
        except InvalidEmailError as e:
            print(e)


# =====================================================
# Select object by ID helper
# =====================================================
def select_by_id(
    items: list, prompt: str = "Enter ID", display_attr: str = "full_name"
) -> Optional:
    """
    Allow user to select an object from a list by its ID.
    """

    # No selectable items
    if not items:
        print("No items available.")
        return None

    # Display items sorted by ID
    for item in sorted(items, key=lambda x: getattr(x, "id", 0)):
        display = getattr(item, display_attr)

        # Call attribute if it's a method
        if callable(display):
            display = display()

        print(f"ID {item.id}: {display}")

    while True:
        selection = get_input(prompt)

        # User chose to go back
        if selection is None:
            return None

        try:
            # Convert input to ID and find matching object
            sel_id = int(selection)
            selected = next(x for x in items if x.id == sel_id)
            return selected

        except (ValueError, StopIteration):
            print("Invalid ID. Try again.")


# =====================================================
# Menu choice helper
# =====================================================
def get_menu_choice(prompt: str, valid_choices: list[str]) -> Optional[str]:
    """
    Prompt user until a valid menu option is selected.
    """

    while True:
        choice = get_input(prompt)

        # User chose to go back
        if choice is None:
            return None

        # Valid menu option
        if choice in valid_choices:
            return choice

        print(f"Invalid choice. Enter one of: {', '.join(valid_choices)}")


# =====================================================
# Internal helpers for email tracking
# =====================================================
def max_reminders(student: Student) -> int:
    """
    Determine how many reminder emails are expected for a student.
    """

    # Trimestral plans require 3 reminders
    if student.payment_plan and student.payment_plan.is_trimestral:
        return 3

    # Yearly plans only require 1
    return 1


def ensure_email_log_exists(email_log: Dict, student: Student) -> None:
    """
    Ensure email_log has a properly sized entry for a student.
    """

    sid = student.id
    n = max_reminders(student)

    # Create new entry if missing
    if sid not in email_log:
        email_log[sid] = {
            "welcome": 0,
            "reminder": [0] * n,
            "thank_you": [0] * n,
        }
        return

    entry = email_log[sid]

    # Ensure welcome counter exists
    if "welcome" not in entry:
        entry["welcome"] = 0

    # Ensure reminder list matches expected size
    reminders = entry.get("reminder", [])
    if len(reminders) != n:
        entry["reminder"] = (reminders + [0] * n)[:n]

    # Ensure thank-you list matches expected size
    thank_you = entry.get("thank_you", [])
    if len(thank_you) != n:
        entry["thank_you"] = (thank_you + [0] * n)[:n]
