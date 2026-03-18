from typing import List, Optional
from person import Person
from payment import PaymentPlan


# =====================================================
# Student Class
# =====================================================
class Student(Person):
    """
    Represents a student in the school.
    Inherits basic personal data from Person.
    """

    def __init__(self, *args, id: int | None = None) -> None:
        """
        Initialize a Student instance.
        Args:
            id (int | None): Optional existing ID (useful when loading saved data).
        """
        # Initialize Person attributes (id, name, surname, etc.)
        super().__init__(*args, id=id)

        # List of courses the student is enrolled in
        self.courses: List["Course"] = []

        # Payment plan associated with the student (if any)
        self.payment_plan: Optional[PaymentPlan] = None

    # -------------------------
    # Course management
    # -------------------------
    def enroll_course(self, course: "Course") -> None:
        """
        Enroll the student in a course.
        """
        # Local import to avoid circular dependency
        from course import Course

        # Prevent duplicate enrollments
        if course in self.courses:
            raise ValueError(f"Already enrolled in {course.name}")

        # Prevent enrollment changes after payments started
        if self.payment_plan and self.payment_plan.has_payments():
            raise RuntimeError(f"Cannot enroll in {course.name}; payment plan started")

        # Update payment plan to reflect new number of courses
        if self.payment_plan:
            self.payment_plan.update_for_courses(self.total_courses + 1)

        # Add course to student's course list
        self.courses.append(course)

        # Ensure student is also added to course's student list
        if self not in course.students:
            course.students.append(self)

    def disenroll_course(self, course: "Course") -> None:
        """
        Remove the student from a course.
        """
        # Local import to avoid circular dependency
        from course import Course

        # Ensure the student is actually enrolled
        if course not in self.courses:
            raise ValueError(f"Not enrolled in {course.name}")

        # Prevent disenrollment if payments already started
        if self.payment_plan and self.payment_plan.has_payments():
            raise RuntimeError(
                f"Cannot disenroll from {course.name}; payment plan started"
            )

        # Update payment plan to reflect reduced number of courses
        if self.payment_plan:
            self.payment_plan.update_for_courses(self.total_courses - 1)

        # Remove course from student's course list
        self.courses.remove(course)

        # Ensure student is also removed from course's student list
        if self in course.students:
            course.students.remove(self)

    # -------------------------
    # Convenience properties
    # -------------------------
    @property
    def total_courses(self) -> int:
        """
        Return the number of courses the student is enrolled in.
        """
        return len(self.courses)

    @property
    def course_names(self) -> str:
        """
        Return a comma-separated list of course names.
        """
        # If no courses, return a placeholder
        if not self.courses:
            return "-"

        # Join course names for display or reports
        return ", ".join(c.name for c in self.courses)
