from typing import List
from person import Person


# =====================================================
# Teacher Class
# =====================================================
class Teacher(Person):
    """Represents a teacher in the school.

    Attributes:
        courses (List[Course]): Courses the teacher teaches.
    """

    def __init__(self, *args, id: int | None = None) -> None:
        """
        Initialize a Teacher.

        Args:
            *args: Passed to Person constructor (name, surname, email, phone, birth_date)
            id (int | None): Optional existing ID (useful when loading saved data).
        """
        # Initialize Person attributes (id, name, surname, etc.)
        super().__init__(*args, id=id)

        # List of courses the teacher teaches
        self.courses: List["Course"] = []

    # -------------------------
    # Course assignment
    # -------------------------
    def assign_course(self, course: "Course") -> None:
        """
        Assign a course to the teacher.

        Args:
            course (Course): Course to assign.

        Why:
            Keeps both teacher.courses and course.teacher consistent.
        """
        from course import Course  # Local import to avoid circular import

        if course not in self.courses:
            self.courses.append(course)
            if getattr(course, "teacher", None) is not self:
                course.assign_teacher(self)

    def remove_course(self, course: "Course") -> None:
        """
        Remove a course from the teacher.

        Args:
            course (Course): Course to remove.

        Why:
            Keeps both teacher.courses and course.teacher consistent.
        """
        from course import Course  # Local import to avoid circular import

        if course in self.courses:
            self.courses.remove(course)
            if getattr(course, "teacher", None) is self:
                course.teacher = None

    # -------------------------
    # Convenience properties
    # -------------------------
    @property
    def course_names(self) -> str:
        """Return a comma-separated string of all course names the teacher teaches."""
        if not self.courses:
            return "-"
        return ", ".join(c.name for c in self.courses)
