from datetime import date


class Person:
    """Represents a person with basic personal information.

    Attributes:
        id (int): Unique identifier for the person (auto-incremented).
        name (str): First name of the person.
        surname (str): Last name of the person.
        email (str): Email address.
        phone (str): Phone number.
        birth_date (date): Birth date of the person.
    """

    # Class-level counter used to generate unique IDs for Person objects
    _id_counter: int = 0

    def __init__(
        self,
        name: str,
        surname: str,
        email: str,
        phone: str,
        birth_date: date,
        id: int | None = None,
    ) -> None:
        """
        Initialize a Person instance.

        Args:
            name (str): First name.
            surname (str): Last name.
            email (str): Email address.
            phone (str): Phone number.
            birth_date (date): Birth date.
        """

        if id is not None:
            self.id = id
            # Update the counter if loaded ID is higher
            if id >= Person._id_counter:
                Person._id_counter = id + 1
        else:
            self.id = Person._id_counter
            Person._id_counter += 1

        # Store personal information
        self.name: str = name
        self.surname: str = surname
        self.email: str = email
        self.phone: str = phone
        self.birth_date: date = birth_date

    @property
    def age(self) -> int:
        """
        Calculate the current age of the person.

        Returns:
            int: Age in years.
        """

        # Get today's date
        today = date.today()

        # Calculate age:
        # - difference in years
        # - subtract 1 if birthday hasn't happened yet this year
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    def full_name(self) -> str:
        """
        Get the full name of the person.

        Returns:
            str: "Name Surname"
        """

        # Combine name and surname for display purposes
        return f"{self.name} {self.surname}"

    @classmethod
    def reset_id_counter(cls) -> None:
        """Reset counter to 0 (useful for full reset of system)."""
        cls._id_counter = 0
