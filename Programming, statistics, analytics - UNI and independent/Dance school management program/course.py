from typing import List, Optional


class Course:
    """Represents a course in the school.

    Attributes:
        id (int): Unique ID for each course.
        name (str): Name of the course.
        teacher (Optional[Teacher]): Teacher assigned to the course.
        students (List[Student]): List of students enrolled in the course.
    """

    # Class-level counter used to generate unique IDs for each Course instance
    _id_counter: int = 0

    def __init__(self, name: str, teacher: Optional["Teacher"] = None) -> None:
        """
        Initialize a Course.

        Args:
            name (str): Name of the course.
            teacher (Optional[Teacher]): Teacher to assign immediately.
        """

        # Normalize name: first letter uppercase, rest lowercase
        self.name: str = name.strip().capitalize()

        # Assign a unique ID using the class-level counter
        self.id: int = Course._id_counter

        # Increment the counter so the next course gets a new ID
        Course._id_counter += 1

        # Store the course name
        self.name: str = name

        # Teacher is initially None until assigned
        self.teacher: Optional["Teacher"] = None

        # List that will contain enrolled students
        self.students: List["Student"] = []

        # If a teacher was provided at creation time, assign them
        if teacher is not None:
            self.assign_teacher(teacher)

    def add_student(self, student: "Student") -> None:
        """
        Enroll a student in this course, maintaining both sides.

        Args:
            student (Student): Student to add.
        """

        # Add student to this course only if not already enrolled
        if student not in self.students:
            self.students.append(student)

        # Also add this course to the student's list of courses
        # This keeps the relationship consistent in both objects
        if self not in student.courses:
            student.courses.append(self)

    def remove_student(self, student: "Student") -> None:
        """
        Remove a student from this course, maintaining both sides.

        Args:
            student (Student): Student to remove.
        """

        # Remove the student from the course's student list if present
        if student in self.students:
            self.students.remove(student)

        # Also remove this course from the student's courses list
        # This avoids dangling references
        if self in student.courses:
            student.courses.remove(self)

    def assign_teacher(self, teacher: "Teacher") -> None:
        """
        Assign a teacher to this course and update teacher's courses.

        Args:
            teacher (Teacher): Teacher to assign.
        """

        # Local import to avoid circular import issues (Teacher imports Course)
        from teacher import Teacher

        # If the course already had a teacher, remove this course
        # from the old teacher's course list
        if self.teacher is not None and self in self.teacher.courses:
            self.teacher.courses.remove(self)

        # Assign the new teacher to this course
        self.teacher = teacher

        # Ensure the course is listed in the new teacher's courses
        if self not in teacher.courses:
            teacher.courses.append(self)

    @classmethod
    def reset_id_counter(cls) -> None:
        """Reset course ID counter to 0 (useful for full reset)."""
        cls._id_counter = 0

    @classmethod
    def set_id_counter(cls, counter: int) -> None:
        """Set the counter to a specific value (used after loading)."""
        cls._id_counter = counter
