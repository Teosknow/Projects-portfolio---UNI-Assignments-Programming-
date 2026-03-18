from student import Student
from teacher import Teacher
from course import Course
from payment import PaymentPlan
from tabulate import tabulate  # For nicely formatted tables
from typing import List, Dict, Any
from datetime import date

import emails
from utils import (
    get_menu_choice,
    get_input,
    get_date_input,
    get_email_input,
    select_by_id,
    max_reminders,
    ensure_email_log_exists,
)


class SchoolManager:
    """
    Manages the core operations of the school:
    - Students, teachers, courses
    - Payment plans and installments
    - Email generation and tracking
    """

    def __init__(self) -> None:
        # Lists holding core entities of the system
        self.students: List[Student] = []
        self.teachers: List[Teacher] = []
        self.courses: List[Course] = []

        # Basic school information used in displays / emails
        self.school_name: str = "My Dance School"
        self.contact_info: str = "Email: info@dance.com | Phone: 123-456-7890"

        # Email tracking structure:
        # student_id -> {
        #   'welcome': int,
        #   'reminder': List[int],
        #   'thank_you': List[int]
        # }
        self.email_log: Dict[int, Dict[str, Any]] = {}

    # ====================================================
    # Basic Add Methods
    # ====================================================
    def add_student(self, student: Student) -> None:
        """
        Add a new student to the system.

        Checks for duplicates (same name, surname, birth date) and
        initializes email tracking.
        """

        # Check for duplicate student based on identity fields
        for s in self.students:
            if (
                s.name.lower() == student.name.lower()
                and s.surname.lower() == student.surname.lower()
                and s.birth_date == student.birth_date
            ):
                raise ValueError(
                    f"Student {student.full_name()} with birth date {student.birth_date} already exists."
                )

        # Add student to internal list
        self.students.append(student)

        # Initialize email tracking entry for this student
        ensure_email_log_exists(self.email_log, student)

    def add_teacher(self, teacher: Teacher) -> None:
        """
        Add a new teacher to the system.

        Duplicate prevention is based on name, surname, and birth date.
        """

        # Check for duplicate teacher
        for t in self.teachers:
            if (
                t.name.lower() == teacher.name.lower()
                and t.surname.lower() == teacher.surname.lower()
                and t.birth_date == teacher.birth_date
            ):
                raise ValueError(
                    f"Teacher {teacher.full_name()} with birth date {teacher.birth_date} already exists."
                )

        # Add teacher to internal list
        self.teachers.append(teacher)

    def add_course(self, course: Course) -> None:
        """
        Add a new course to the system.

        Duplicate course names (case-insensitive) are not allowed.
        """

        # Prevent duplicate courses by name
        for c in self.courses:
            if c.name.strip().lower() == course.name.strip().lower():
                raise ValueError(f"Course '{course.name}' already exists.")

        # Add course to internal list
        self.courses.append(course)

    # -------------------- Courses Table --------------------
    def create_courses_table(self) -> None:
        """Display all courses, number of students, and assigned teacher."""
        if not self.courses:
            print("No courses available.")
            return

        headers = ["Course Name", "Number of Students", "Teacher"]
        table = []

        for c in sorted(self.courses, key=lambda x: x.name.lower()):
            student_count = len(c.students)
            teacher_name = c.teacher.full_name() if c.teacher else "No teacher assigned"
            table.append([c.name, student_count, teacher_name])

        print(tabulate(table, headers=headers, tablefmt="grid"))

    # ====================================================
    # Student Tables
    # ====================================================
    def create_students_table(self) -> None:
        """
        Display all students in a formatted table, sorted by surname then name.

        Shows ID, name, birth date, age, email, phone, and enrolled courses.
        """

        # No students to display
        if not self.students:
            print("No students available.")
            return

        # Column headers for the table
        headers = [
            "ID",
            "Name",
            "Surname",
            "Birth Date",
            "Age",
            "Email",
            "Phone",
            "Courses",
        ]

        table = []

        # Sort students alphabetically by surname, then name
        for s in sorted(
            self.students, key=lambda x: (x.surname.lower(), x.name.lower())
        ):
            # Get course names safely (property if available, fallback otherwise)
            courses = (
                s.course_names
                if hasattr(s, "course_names")
                else (", ".join(c.name for c in s.courses) if s.courses else "-")
            )

            # Add one row per student
            table.append(
                [
                    s.id,
                    s.name,
                    s.surname,
                    s.birth_date.strftime("%Y-%m-%d"),
                    s.age,
                    s.email,
                    s.phone,
                    courses,
                ]
            )

        # Print formatted table
        print(tabulate(table, headers=headers, tablefmt="grid"))

    def create_students_by_course_table(self) -> None:
        """
        Display students grouped by course with counts.

        Skips courses with no students. Shows student ID, name, birth date, age, email, phone.
        """

        # No courses defined
        if not self.courses:
            print("No courses available.")
            return

        # Iterate through each course
        for course in self.courses:
            # Skip courses with no enrolled students
            if not course.students:
                continue

            headers = ["ID", "Name", "Surname", "Birth Date", "Age", "Email", "Phone"]
            table = []

            # Sort students inside the course
            for s in sorted(
                course.students, key=lambda x: (x.surname.lower(), x.name.lower())
            ):
                table.append(
                    [
                        s.id,
                        s.name,
                        s.surname,
                        s.birth_date.strftime("%Y-%m-%d"),
                        s.age,
                        s.email,
                        s.phone,
                    ]
                )

            # Print course-specific table
            print(f"\nCourse: {course.name}")
            print(tabulate(table, headers=headers, tablefmt="grid"))
            print(f"Total students in {course.name}: {len(course.students)}")

    # ====================================================
    # Teacher Tables
    # ====================================================
    def create_teachers_table(self) -> None:
        """
        Display all teachers in a formatted table with their assigned courses.
        """

        # No teachers to display
        if not self.teachers:
            print("No teachers available.")
            return

        headers = [
            "ID",
            "Name",
            "Surname",
            "Birth Date",
            "Age",
            "Email",
            "Phone",
            "Courses",
        ]

        table = []

        # Sort teachers alphabetically
        for t in sorted(
            self.teachers, key=lambda x: (x.surname.lower(), x.name.lower())
        ):
            # Get list of assigned courses
            courses = (
                t.course_names
                if hasattr(t, "course_names")
                else (", ".join(c.name for c in t.courses) if t.courses else "-")
            )

            table.append(
                [
                    t.id,
                    t.name,
                    t.surname,
                    t.birth_date.strftime("%Y-%m-%d"),
                    t.age,
                    t.email,
                    t.phone,
                    courses,
                ]
            )

        # Print formatted table
        print(tabulate(table, headers=headers, tablefmt="grid"))

    # ====================================================
    # Payment Tables
    # ====================================================

    def change_payment_status(self) -> None:
        """
        Mark a specific installment as PAID or revert it to DUE.

        Workflow:
            - Select a student by ID.
            - List installments with their current status.
            - Select installment to change.
            - Confirm action and optionally choose payment date if marking PAID.
        """
        if not self.students:
            print("No students available.")
            return

        # Select the student
        student = select_by_id(self.students, "Enter student ID")
        if student is None or not student.payment_plan:
            print(f"No payment plan set for {student.full_name()}.")
            return

        # Display installments
        print("\nInstallments:")
        for idx, inst in enumerate(student.payment_plan.installments):
            paid_info = (
                f"(PAID on {inst.paid_date})"
                if getattr(inst, "paid_date", None)
                else inst.status
            )
            print(
                f"{idx} - Amount: {inst.amount:.2f} €, Due: {inst.due_date}, Status: {paid_info}"
            )

        # Get installment index
        inst_idx_input = get_input("Enter installment index to change status")
        if inst_idx_input is None:
            return
        try:
            inst_idx = int(inst_idx_input)
            inst = student.payment_plan.installments[inst_idx]
        except (ValueError, IndexError):
            print("Invalid installment index.")
            return

        if inst.paid:
            # Option to revert to DUE
            print(f"Warning: Installment {inst_idx + 1} is already marked PAID.")
            confirm = get_menu_choice(
                "Do you want to revert it back to DUE? (Y/N)", ["y", "Y", "n", "N"]
            )
            if confirm is None or confirm.lower() != "y":
                print("No changes made.")
                return
            inst.paid = False
            if hasattr(inst, "paid_date"):
                delattr(inst, "paid_date")
            print(
                f"Installment {inst_idx + 1} for {student.full_name()} reverted to DUE."
            )
        else:
            # Option to mark as PAID
            confirm = get_menu_choice(
                f"Mark installment {inst_idx + 1} as PAID? (Y/N)", ["y", "Y", "n", "N"]
            )
            if confirm is None or confirm.lower() != "y":
                print("No changes made.")
                return

            # Choose date
            print("1 - Use today's date")
            print("2 - Enter manually")
            date_choice = get_menu_choice("Select option", ["1", "2"])
            if date_choice is None:
                print("No changes made.")
                return

            if date_choice == "1":
                paid_date = date.today()
            else:
                paid_date = get_date_input("Payment")
                if paid_date is None:
                    print("No changes made.")
                    return

            inst.paid = True
            inst.paid_date = paid_date
            print(
                f"Installment {inst_idx + 1} for {student.full_name()} marked as PAID on {inst.paid_date}."
            )

    def create_payments_table(self) -> None:
        """
        Display detailed payment information for all students.

        Shows each installment with amount, due date, and status (PAID/DUE).
        """

        # Exit early if there are no students
        if not self.students:
            print("No students available.")
            return

        # Column headers for the detailed payment table
        headers = [
            "ID",
            "Student Name",
            "Surname",
            "Courses",
            "Payment Type",
            "Installment #",
            "Amount (€)",
            "Due Date",
            "Status",
        ]
        table = []

        # Sort students alphabetically by surname and name
        for s in sorted(
            self.students, key=lambda x: (x.surname.lower(), x.name.lower())
        ):
            # Resolve course names safely
            courses = (
                s.course_names
                if hasattr(s, "course_names")
                else (", ".join(c.name for c in s.courses) if s.courses else "-")
            )

            # Case: student has no payment plan
            if not s.payment_plan:
                table.append(
                    [s.id, s.name, s.surname, courses, "-", "-", "-", "-", "-"]
                )
            else:
                # One row per installment
                for i, inst in enumerate(s.payment_plan.installments):
                    table.append(
                        [
                            s.id,
                            s.name,
                            s.surname,
                            courses,
                            s.payment_plan.payment_type.upper(),
                            i + 1,
                            inst.amount,
                            inst.due_date.strftime("%Y-%m-%d"),
                            inst.status,
                        ]
                    )

        # Print the full table
        print(tabulate(table, headers=headers, tablefmt="grid"))

    def create_students_payment_summary_table(self) -> None:
        """
        Display a compact overview of student payments:
        - YEARLY: single row per student, one installment
        - TRIMESTRAL: single row per student, bullets per installment inside the same cell
        """

        # Exit early if there are no students
        if not self.students:
            print("No students available.")
            return

        # Headers for both yearly and trimestral tables
        yearly_headers = [
            "ID",
            "Student Name",
            "Surname",
            "Courses",
            "Installment (€)",
            "Due Date",
            "Status",
        ]
        trimestral_headers = yearly_headers.copy()

        yearly_table = []
        trimestral_table = []

        # Iterate over students in sorted order
        for s in sorted(
            self.students, key=lambda x: (x.surname.lower(), x.name.lower())
        ):
            courses = ", ".join(c.name for c in s.courses) if s.courses else "-"

            # Case: no payment plan
            if not s.payment_plan:
                row = [s.id, s.name, s.surname, courses, "-", "-", "-"]
                yearly_table.append(row)
                trimestral_table.append(row)
                continue

            plan = s.payment_plan

            # YEARLY payment plan: single installment
            if plan.payment_type.upper() == "YEARLY":
                inst = plan.installments[0] if plan.installments else None
                amount = f"{inst.amount:.2f}" if inst else "-"
                due_date = inst.due_date.strftime("%Y-%m-%d") if inst else "-"
                status = inst.status if inst else "-"
                yearly_table.append(
                    [s.id, s.name, s.surname, courses, amount, due_date, status]
                )

            # TRIMESTRAL payment plan: multiple installments shown vertically
            elif plan.payment_type.upper() == "TRIMESTRAL":
                amounts = "\n".join(
                    f"{i+1}^ {inst.amount:.2f}"
                    for i, inst in enumerate(plan.installments)
                )
                due_dates = "\n".join(
                    f"{i+1}^ {inst.due_date.strftime('%Y-%m-%d')}"
                    for i, inst in enumerate(plan.installments)
                )
                statuses = "\n".join(
                    f"{i+1}^ {inst.status}" for i, inst in enumerate(plan.installments)
                )
                trimestral_table.append(
                    [s.id, s.name, s.surname, courses, amounts, due_dates, statuses]
                )

        # Print yearly table if present
        if yearly_table:
            print("\nPAYMENT PLAN: YEARLY\n")
            print(tabulate(yearly_table, headers=yearly_headers, tablefmt="grid"))

        # Print trimestral table if present
        if trimestral_table:
            print("\nPAYMENT PLAN: TRIMESTRAL\n")
            print(
                tabulate(trimestral_table, headers=trimestral_headers, tablefmt="grid")
            )

    def create_students_with_unpaid_table(self) -> None:
        """
        Display only students with unpaid installments.
        - YEARLY: single row per student
        - TRIMESTRAL: single row per student with bullets per installment
        """

        # Exit early if there are no students
        if not self.students:
            print("No students available.")
            return

        yearly_headers = [
            "ID",
            "Student Name",
            "Surname",
            "Courses",
            "Installment (€)",
            "Due Date",
            "Status",
        ]
        trimestral_headers = yearly_headers.copy()

        yearly_table = []
        trimestral_table = []

        # Iterate over students in sorted order
        for s in sorted(
            self.students, key=lambda x: (x.surname.lower(), x.name.lower())
        ):
            # Skip students without unpaid installments
            if not s.payment_plan or s.payment_plan.unpaid_amount == 0:
                continue

            courses = ", ".join(c.name for c in s.courses) if s.courses else "-"
            plan = s.payment_plan

            # Filter unpaid installments
            unpaid_inst = [inst for inst in plan.installments if not inst.paid]

            # YEARLY unpaid case
            if plan.payment_type.upper() == "YEARLY":
                inst = unpaid_inst[0] if unpaid_inst else None
                amount = f"{inst.amount:.2f}" if inst else "-"
                due_date = inst.due_date.strftime("%Y-%m-%d") if inst else "-"
                status = inst.status if inst else "-"
                yearly_table.append(
                    [s.id, s.name, s.surname, courses, amount, due_date, status]
                )

            # TRIMESTRAL unpaid case
            elif plan.payment_type.upper() == "TRIMESTRAL":
                amounts = "\n".join(
                    f"{i+1}^ {inst.amount:.2f}" for i, inst in enumerate(unpaid_inst)
                )
                due_dates = "\n".join(
                    f"{i+1}^ {inst.due_date.strftime('%Y-%m-%d')}"
                    for i, inst in enumerate(unpaid_inst)
                )
                statuses = "\n".join(
                    f"{i+1}^ {inst.status}" for i, inst in enumerate(unpaid_inst)
                )
                trimestral_table.append(
                    [s.id, s.name, s.surname, courses, amounts, due_dates, statuses]
                )

        # Print unpaid yearly table
        if yearly_table:
            print("\nPAYMENT PLAN: YEARLY (Unpaid)\n")
            print(tabulate(yearly_table, headers=yearly_headers, tablefmt="grid"))

        # Print unpaid trimestral table
        if trimestral_table:
            print("\nPAYMENT PLAN: TRIMESTRAL (Unpaid)\n")
            print(
                tabulate(trimestral_table, headers=trimestral_headers, tablefmt="grid")
            )

        # Fallback message if everyone has paid
        if not yearly_table and not trimestral_table:
            print("All students have paid their installments.")

    def show_student_payment_info(self, student: Student) -> None:
        """
        Display detailed payment info for a single student:
        - Student info: ID, name, email, phone, courses, payment type
        - Table of installments: amount, due date, status, payment date
        """

        # Guard: student has no payment plan
        if not student.payment_plan:
            print(f"No payment plan set for {student.full_name()}.")
            return

        # Print basic student information
        print(f"\nStudent ID: {student.id}")
        print(f"Student: {student.full_name()}")
        print(f"Email: {student.email}")
        print(f"Phone: {student.phone}")
        print(f"Courses: {student.course_names}")
        print(f"Payment Type: {student.payment_plan.payment_type.upper()}")

        headers = ["Installment #", "Amount (€)", "Due Date", "Status", "Payment Date"]
        table = []

        # One row per installment
        for i, inst in enumerate(student.payment_plan.installments):
            table.append(
                [
                    i + 1,
                    inst.amount,
                    inst.due_date.strftime("%Y-%m-%d"),
                    inst.status,
                    inst.paid_date.strftime("%Y-%m-%d") if inst.paid_date else "-",
                ]
            )

        # Print installment table
        print(tabulate(table, headers=headers, tablefmt="grid"))

    # ====================================================
    # Generate Emails
    # ====================================================
    def generate_welcome_email(self, student: Student) -> str:
        """
        Generate (and return) a welcome email for a student.
        Always returns the email text; if welcome was already generated before,
        the returned text is prefixed with a warning (but the email is still shown).
        """

        # Ensure the email log structure exists for this student
        ensure_email_log_exists(self.email_log, student)
        log = self.email_log[student.id]

        # Shortcut reference to the student's payment plan
        plan = student.payment_plan

        # Build a readable list of "amount + due date" strings
        # Used inside the welcome email body
        amounts_dates = (
            [
                f"{i.amount:.2f} € on {i.due_date.strftime('%Y-%m-%d')}"
                for i in plan.installments
            ]
            if plan
            else []
        )

        # Generate the welcome email using the template function
        email_content = emails.welcome_email(
            student.name,
            student.surname,
            [c.name for c in student.courses],
            plan.payment_type.upper() if plan else "N/A",
            amounts_dates,
            self.school_name,
            self.contact_info,
        )

        # If a welcome email was already generated before,
        # return the email but prepend a warning
        if log.get("welcome", 0) >= 1:
            warning = (
                "Warning: Welcome email has already been generated for this student."
            )
            return f"{warning}\n\n{email_content}"

        # First time generation → mark welcome email as sent
        log["welcome"] = 1
        return email_content

    def generate_reminder_email(self, student: Student, installment_index: int) -> str:
        """
        Generate (and return) a reminder email for a specific installment.
        - If the installment is already paid: returns a clear message and does NOT generate a reminder.
        - If the reminder was already generated: still returns the email but prefixed with a warning.
        - Otherwise generates the email and marks that reminder as sent.
        """

        # Ensure email tracking exists
        ensure_email_log_exists(self.email_log, student)
        log = self.email_log[student.id]

        # Payment plan must exist
        plan = student.payment_plan
        if not plan:
            return "Cannot generate reminder: no payment plan set for this student."

        # Validate installment index
        if not (0 <= installment_index < len(plan.installments)):
            return "Invalid installment index."

        inst = plan.installments[installment_index]

        # Do not send reminders for already paid installments
        if inst.paid:
            return f"Cannot generate reminder: Installment {installment_index + 1} is already PAID."

        # If reminder already generated before → still generate email, but warn
        if log["reminder"][installment_index]:
            warning = f"Warning: Reminder email for installment {installment_index + 1} was already generated."
            email_content = emails.reminder_email(
                student.name,
                student.surname,
                f"{inst.amount:.2f} €",
                inst.due_date,
                self.school_name,
                self.contact_info,
            )
            return f"{warning}\n\n{email_content}"

        # First reminder generation → create email and mark as sent
        email_content = emails.reminder_email(
            student.name,
            student.surname,
            f"{inst.amount:.2f} €",
            inst.due_date,
            self.school_name,
            self.contact_info,
        )
        log["reminder"][installment_index] = 1
        return email_content

    def generate_thank_you_email(self, student: Student, installment_index: int) -> str:
        """
        Generate a thank-you email for a specific installment.

        Args:
            student (Student): The student for whom to generate the email.
            installment_index (int): 0-based index of the installment.

        Returns:
            str: Email content or a warning message if cannot be generated.
        """
        ensure_email_log_exists(self.email_log, student)
        log = self.email_log[student.id]

        plan = student.payment_plan
        if not plan:
            return "No payment plan set for this student."

        if not (0 <= installment_index < len(plan.installments)):
            return "Invalid installment index."

        inst = plan.installments[installment_index]
        if not inst.paid:
            return f"Cannot generate thank-you email: Installment {installment_index + 1} not paid yet."

        if log["thank_you"][installment_index]:
            return f"Warning: Thank-you email for installment {installment_index + 1} was already generated."

        # Pass only the objects that the template function expects
        remaining_installments = [i for i in plan.installments if not i.paid]

        email_content = emails.thank_you_email(
            student.name,
            student.surname,
            inst,  # the Installment object that was just paid
            remaining_installments,  # list of remaining unpaid Installments
            self.school_name,
            self.contact_info,
        )

        log["thank_you"][installment_index] = 1
        return email_content

    # ====================================================
    # Reporting Tables
    # ====================================================
    def email_status_table(self) -> None:
        """
        Print a table summarizing email statuses for all students.

        Columns:
            Student | Plan | Welcome Sent | Reminder Sent | Thank You Sent
        """

        headers = ["Student", "Plan", "Welcome Sent", "Reminder Sent", "Thank You Sent"]
        rows = []

        # Iterate over all students
        for s in self.students:
            log = self.email_log.get(s.id, {})
            plan_type = s.payment_plan.payment_type.upper() if s.payment_plan else "N/A"
            max_inst = max_reminders(s)

            # Extract reminder and thank-you arrays
            reminders = log.get("reminder", [])
            thankyous = log.get("thank_you", [])

            # Count how many reminders and thank-you emails were sent
            reminders_sent = sum(reminders) if isinstance(reminders, list) else 0
            thanks_sent = sum(thankyous) if isinstance(thankyous, list) else 0

            # Append row with summary info
            rows.append(
                [
                    s.full_name(),
                    plan_type,
                    "✓" if log.get("welcome", 0) else "",
                    f"{reminders_sent}/{max_inst}",
                    f"{thanks_sent}/{max_inst}",
                ]
            )

        # Print summary table
        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def pending_email_table(self) -> None:
        """
        Print a table showing pending emails for each student.

        Columns:
            Student | Plan | Pending Emails
        """

        headers = ["Student", "Plan", "Pending Emails"]
        rows = []

        # Iterate over all students
        for s in self.students:
            log = self.email_log.get(s.id, {})
            plan_type = s.payment_plan.payment_type.upper() if s.payment_plan else "N/A"
            max_inst = max_reminders(s)

            pending = []

            # Check welcome email
            if log.get("welcome", 0) == 0:
                pending.append("Welcome")

            # Check reminder emails
            reminders = log.get("reminder", [])
            for i in range(max_inst):
                if i >= len(reminders) or reminders[i] == 0:
                    pending.append(f"Reminder {i+1}")

            # Check thank-you emails
            thankyous = log.get("thank_you", [])
            for i in range(max_inst):
                if i >= len(thankyous) or thankyous[i] == 0:
                    pending.append(f"Thank You {i+1}")

            # Add row only if something is pending
            if pending:
                rows.append([s.full_name(), plan_type, ", ".join(pending)])

        # Print table or fallback message
        if rows:
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        else:
            print("All students have sent emails for all installments.")
