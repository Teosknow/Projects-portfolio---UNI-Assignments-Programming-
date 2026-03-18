from datetime import date
from person import Person
from student import Student
from teacher import Teacher
from course import Course
from payment import PaymentPlan
from school_manager import SchoolManager
from tabulate import tabulate
from typing import Optional, Callable
import emails
from utils import (
    get_menu_choice,
    get_input,
    get_date_input,
    get_email_input,
    select_by_id,
)
from storage import load_manager, save_manager


# -------------------------
# Load saved data at the start
# -------------------------

manager = load_manager()

if not manager.courses and not manager.students and not manager.teachers:

    def initialize_sample_data(mgr: "SchoolManager") -> None:
        """Add default courses, teachers, students, and payment plans."""
        from person import Person

        # Reset the ID counter before creating any objects
        Person.reset_id_counter()

        # Sample courses
        courses = [Course(name) for name in ["Pilates", "Hip Hop", "Ballet"]]
        for c in courses:
            mgr.add_course(c)

        # Sample teachers
        teacher1 = Teacher(
            "Luisa", "Vitton", "luisa@example.com", "1234567890", date(1985, 4, 12)
        )
        teacher2 = Teacher(
            "Marco", "Rossi", "marco@example.com", "0987654321", date(1990, 8, 23)
        )
        mgr.add_teacher(teacher1)
        mgr.add_teacher(teacher2)

        teacher1.assign_course(courses[0])
        teacher2.assign_course(courses[1])

        # Sample students
        student1 = Student(
            "Teo", "Ata", "teo@example.com", "111222333", date(2000, 1, 15)
        )
        student2 = Student(
            "Giulia", "Riga", "riga@example.com", "444555666", date(1999, 6, 20)
        )
        student3 = Student(
            "Alice", "Miller", "alice@example.com", "777888999", date(2001, 12, 5)
        )
        for s in [student1, student2, student3]:
            mgr.add_student(s)

        # Assign students to courses
        courses[0].add_student(student1)
        courses[1].add_student(student2)
        courses[0].add_student(student3)
        courses[2].add_student(student3)

        # Payment plans
        student1.payment_plan = PaymentPlan("TRIMESTRAL", student1.total_courses)
        student2.payment_plan = PaymentPlan("YEARLY", student2.total_courses)
        student3.payment_plan = PaymentPlan("TRIMESTRAL", student3.total_courses)

    initialize_sample_data(manager)
    # save initial sample data immediately so file and counter are consistent
    save_manager(manager)


# -------------------------
# Student menu
# -------------------------
def student_menu(manager: SchoolManager):
    """
    Menu for managing students:
        - Add/remove students
        - Enroll/disenroll in courses
        - View student lists
    Loops until user chooses to go back ('0' or 'b').
    Defensive checks: input validation, back option, empty lists, exceptions.
    """

    while True:
        # Display menu options
        print("\n--- Student Management ---")
        print("Enter 'b' at any time to go back.")
        print("1. Add student")
        print("2. Remove student")
        print("3. Enroll student to course")
        print("4. Disenroll student from course")
        print("5. Show total list of students")
        print("6. Show total list of students by course")
        print("0. Back")

        choice = get_menu_choice("Choice", ["0", "1", "2", "3", "4", "5", "6"])
        if choice is None:  # User chose to go back
            break

        if choice == "1":
            # Add student workflow
            print("Enter 'b' at any time to go back.")
            name = get_input("Name: ")
            if name is None:
                continue
            surname = get_input("Surname: ")
            if surname is None:
                continue
            email = get_email_input()  # Validates format
            if email is None:
                continue
            phone = get_input("Phone: ")
            if phone is None:
                continue
            birth_date = get_date_input("Birth")  # Validates date
            if birth_date is None:
                continue

            student = Student(
                name.strip().capitalize(),
                surname.strip().capitalize(),
                email.lower(),
                phone.strip(),
                birth_date,
            )

            try:
                manager.add_student(student)  # May raise ValueError for duplicates
            except ValueError as e:
                print(e)
                continue

            # persist immediately after mutation
            save_manager(manager)

            print(f"Student {student.full_name()} added.")

        elif choice == "2":
            # Remove student
            print("Enter 'b' at any time to go back.")
            student = select_by_id(manager.students, "Enter student ID to remove")
            if student is None:
                continue
            manager.students.remove(student)
            # persist immediately after mutation
            save_manager(manager)
            print(f"Removed student {student.full_name()}")

        elif choice == "3":
            # Enroll student in course
            print("Enter 'b' at any time to go back.")
            student = select_by_id(manager.students, "Enter student ID to enroll")
            if student is None or not manager.courses:
                print("No students or courses available.")
                continue

            course = select_by_id(manager.courses, "Enter course ID to enroll", "name")
            if course is None:
                continue

            try:
                student.enroll_course(course)  # May raise errors
                # persist immediately after mutation
                save_manager(manager)
                print(f"{student.full_name()} enrolled to {course.name}")
            except (RuntimeError, ValueError) as e:
                print(e)

        elif choice == "4":
            # Disenroll student from course
            print("Enter 'b' at any time to go back.")
            student = select_by_id(manager.students, "Enter student ID to disenroll")
            if student is None or not student.courses:
                print("Student not enrolled in any courses or no students available.")
                continue

            course = select_by_id(
                student.courses, "Enter course ID to disenroll", "name"
            )
            if course is None:
                continue

            student.disenroll_course(course)
            # persist immediately after mutation
            save_manager(manager)
            print(f"{student.full_name()} disenrolled from {course.name}")

        elif choice == "5":
            # Show all students
            manager.create_students_table()

        elif choice == "6":
            # Show students grouped by course
            manager.create_students_by_course_table()

        elif choice == "0":
            # Exit menu
            break


# -------------------------
# Courses menu
# -------------------------
def courses_menu(manager: SchoolManager):
    """
    Menu for managing courses:
        - Add/remove courses
        - View course list
    Loops until user chooses to go back.
    Defensive checks: input validation, back option, empty lists, duplicates.
    """

    while True:
        print("\n--- Courses Management ---")
        print("Enter 'b' at any time to go back.")
        print("1. Add course")
        print("2. Remove course")
        print("3. Show list of courses")
        print("0. Back")

        choice = get_menu_choice("Choice", ["0", "1", "2", "3"])
        if choice is None:
            break

        if choice == "1":
            print("Enter 'b' at any time to go back.")
            name = get_input("Course name: ")
            if name is None:
                continue
            course = Course(name.strip())
            try:
                manager.add_course(course)  # May raise ValueError for duplicates
            except ValueError as e:
                print(e)
                continue
            # persist immediately after mutation
            save_manager(manager)
            print(f"Course {course.name} added.")

        elif choice == "2":
            print("Enter 'b' at any time to go back.")
            course = select_by_id(manager.courses, "Enter course ID to remove", "name")
            if course is None:
                continue
            manager.courses.remove(course)
            # persist immediately after mutation
            save_manager(manager)
            print(f"Removed course {course.name}")

        elif choice == "3":
            manager.create_courses_table()

        elif choice == "0":
            break


# -------------------------
# Teacher menu
# -------------------------
def teacher_menu(manager: SchoolManager):
    """
    Menu for managing teachers:
        - Add/remove teachers
        - Assign teachers to courses
        - View teacher list
    Loops until user chooses to go back.
    Defensive checks: input validation, back option, empty lists, duplicates.
    """

    while True:
        print("\n--- Teacher Management ---")
        print("Enter 'b' at any time to go back.")
        print("1. Add teacher")
        print("2. Remove teacher")
        print("3. Assign teacher to course")
        print("4. Show total list of teachers")
        print("0. Back")

        choice = get_menu_choice("Choice", ["0", "1", "2", "3", "4"])
        if choice is None:
            break

        if choice == "1":
            # Add teacher workflow
            print("Enter 'b' at any time to go back.")
            name = get_input("Name")
            if name is None:
                continue
            surname = get_input("Surname")
            if surname is None:
                continue
            birth_date = get_date_input("Birth")
            if birth_date is None:
                continue
            email = get_email_input()
            if email is None:
                continue
            phone = get_input("Phone")
            if phone is None:
                continue

            teacher = Teacher(
                name.strip().capitalize(),
                surname.strip().capitalize(),
                email.lower(),
                phone.strip(),
                birth_date,
            )
            try:
                manager.add_teacher(teacher)
            except ValueError as e:
                print(e)
                continue

            # persist immediately after mutation
            save_manager(manager)

            print(f"Teacher {teacher.full_name()} added.")

        elif choice == "2":
            print("Enter 'b' at any time to go back.")
            teacher = select_by_id(manager.teachers, "Enter teacher ID to remove")
            if teacher is None:
                continue
            manager.teachers.remove(teacher)
            # persist immediately after mutation
            save_manager(manager)
            print(f"Removed teacher {teacher.full_name()}")

        elif choice == "3":
            # Assign teacher to course
            print("Enter 'b' at any time to go back.")
            course = select_by_id(manager.courses, "Enter course ID to assign", "name")
            if course is None:
                continue
            teacher = select_by_id(manager.teachers, "Enter teacher ID to assign")
            if teacher is None:
                continue
            course.assign_teacher(teacher)
            # persist immediately after mutation
            save_manager(manager)
            print(f"{teacher.full_name()} assigned to {course.name}")

        elif choice == "4":
            manager.create_teachers_table()

        elif choice == "0":
            break


# -------------------------
# Payment menu
# -------------------------
def payment_menu(manager: SchoolManager):
    """
    Menu for managing student payments:
        - Set payment type
        - Show payment info
        - Change payment status
        - Generate tables (all students, unpaid installments)
    Defensive checks:
        - Student existence
        - Prevent changing plans after payments
        - Confirm overwrite if plan exists
        - Input validation and early exits
    """
    while True:
        print("\n--- Payment Management ---")
        print("Enter 'b' at any time to go back.")
        print("1. Select payment type for student")
        print("2. Show payment info for student")
        print("3. Change payment status for student")
        print("4. Generate table: all students with payment info")
        print("5. Generate table: all students with unpaid installments")
        print("0. Back")

        choice = get_menu_choice("Choice", ["0", "1", "2", "3", "4", "5"])
        if choice is None:
            break

        if choice == "1":
            # Assign payment plan
            print("Enter 'b' at any time to go back.")
            student = select_by_id(manager.students, "Enter student ID")
            if student is None:
                continue

            if student.payment_plan and student.payment_plan.has_payments():
                print(
                    f"Payment plan already started for {student.full_name()}. Cannot modify."
                )
                continue

            if student.payment_plan:
                confirm = get_menu_choice(
                    f"{student.full_name()} already has a plan. Overwrite? (Y/N)",
                    ["y", "Y", "n", "N"],
                )
                if confirm is None or confirm.lower() != "y":
                    print("Payment plan not changed.")
                    continue

            # Select type
            while True:
                print("Select payment type:\n0 - Yearly\n1 - Trimestral")
                p_input = get_menu_choice("Choice", ["0", "1"])
                if p_input is None:
                    break
                payment_type = "YEARLY" if p_input == "0" else "TRIMESTRAL"
                manager.set_student_payment_plan(student, payment_type)
                # persist immediately after mutation
                save_manager(manager)
                break

        elif choice == "2":
            # Show info
            print("Enter 'b' at any time to go back.")
            student = select_by_id(manager.students, "Enter student ID")
            if student is None:
                continue
            if not student.payment_plan:
                print(f"No payment plan set for {student.full_name()}.")
                continue
            manager.show_student_payment_info(student)

        elif choice == "3":
            # Modify status
            print("Enter 'b' at any time to go back.")
            manager.change_payment_status()
            # persist after possible mutation
            save_manager(manager)

        elif choice == "4":
            manager.create_students_payment_summary_table()

        elif choice == "5":
            manager.create_students_with_unpaid_table()

        elif choice == "0":
            break


# -------------------------
# Email menu
# -------------------------
def email_menu(manager: SchoolManager):
    """
    Menu for managing emails:
        - Generate welcome, reminder, and thank-you emails
        - Track email status
        - Show pending emails
    Defensive checks:
        - Student existence
        - Payment plan existence for payment emails
        - Prevent duplicates
        - Validate installment index
    """
    while True:
        print("\n--- Email Management ---")
        print("Enter 'b' at any time to go back.")
        print("1. Generate + print welcome email")
        print("2. Generate + print payment reminder email")
        print("3. Generate + print payment confirmation (thank you) email")
        print("4. Show email tracking table")
        print("5. Show students missing emails")
        print("0. Back")

        choice = get_input("Choice: ")
        if choice is None:
            break

        if choice == "1":
            student = select_by_id(manager.students, "Enter student ID for welcome")
            if student is None:
                continue
            msg = manager.generate_welcome_email(student)
            print("\n" + msg + "\n") if msg else None
            # generate_welcome_email may have modified email_log -> persist
            save_manager(manager)

        elif choice == "2":
            student = select_by_id(manager.students, "Enter student ID for reminder")
            if student is None or not student.payment_plan:
                continue
            # Show installments
            for idx, inst in enumerate(student.payment_plan.installments):
                print(
                    f"{idx} - Amount: {inst.amount:.2f} €, Due: {inst.due_date}, Status: {'PAID' if inst.paid else 'DUE'}"
                )

            idx_input = get_menu_choice(
                "Select installment index for reminder",
                [str(i) for i in range(len(student.payment_plan.installments))],
            )
            if idx_input is None:
                continue
            msg = manager.generate_reminder_email(student, int(idx_input))
            (
                print("\n" + msg + "\n")
                if msg
                else print("Reminder email could not be generated.")
            )
            # generate_reminder_email may have modified email_log -> persist
            save_manager(manager)

        elif choice == "3":
            student = select_by_id(manager.students, "Enter student ID for thank you")
            if student is None or not student.payment_plan:
                continue
            for idx, inst in enumerate(student.payment_plan.installments):
                print(
                    f"{idx} - Amount: {inst.amount:.2f} €, Due: {inst.due_date}, Status: {'PAID' if inst.paid else 'DUE'}"
                )

            idx_input = get_menu_choice(
                "Select installment index for thank-you email",
                [str(i) for i in range(len(student.payment_plan.installments))],
            )
            if idx_input is None:
                continue
            msg = manager.generate_thank_you_email(student, int(idx_input))
            (
                print("\n" + msg + "\n")
                if msg
                else print(
                    f"Warning: Thank you email not sent or installment not paid."
                )
            )
            # generate_thank_you_email may have modified email_log -> persist
            save_manager(manager)

        elif choice == "4":
            manager.email_status_table()

        elif choice == "5":
            manager.pending_email_table()

        elif choice == "0":
            break

        else:
            print("Invalid choice. Please try again.")


# -------------------------
# Reset Data Function
# -------------------------
def reset_all_data() -> Optional[SchoolManager]:
    """
    Reset all data to default examples safely.
    Resets the ID counter and replaces the old manager.
    """
    confirm = get_input(
        "Are you sure you want to reset all data? This cannot be undone (Y/N)"
    )
    if confirm is None or confirm.lower() != "y":
        print("Reset cancelled.")
        return None

    # Reset the global ID counter before creating any new Person and course objects
    Person.reset_id_counter()
    Course.reset_id_counter()

    new_manager = SchoolManager()

    # Initialize sample data in the new manager
    def initialize_sample_data(mgr: "SchoolManager") -> None:
        # Sample courses
        courses = [Course(name) for name in ["Pilates", "Hip Hop", "Ballet"]]
        for c in courses:
            mgr.add_course(c)

        # Sample teachers
        teacher1 = Teacher(
            "Luisa", "Vitton", "luisa@example.com", "1234567890", date(1985, 4, 12)
        )
        teacher2 = Teacher(
            "Marco", "Rossi", "marco@example.com", "0987654321", date(1990, 8, 23)
        )
        mgr.add_teacher(teacher1)
        mgr.add_teacher(teacher2)

        teacher1.assign_course(courses[0])
        teacher2.assign_course(courses[1])

        # Sample students
        student1 = Student(
            "Teo", "Ata", "teo@example.com", "111222333", date(2000, 1, 15)
        )
        student2 = Student(
            "Giulia", "Riga", "riga@example.com", "444555666", date(1999, 6, 20)
        )
        student3 = Student(
            "Alice", "Miller", "alice@example.com", "777888999", date(2001, 12, 5)
        )
        for s in [student1, student2, student3]:
            mgr.add_student(s)

        # Assign students to courses
        courses[0].add_student(student1)
        courses[1].add_student(student2)
        courses[0].add_student(student3)
        courses[2].add_student(student3)

        # Payment plans
        student1.payment_plan = PaymentPlan("TRIMESTRAL", student1.total_courses)
        student2.payment_plan = PaymentPlan("YEARLY", student2.total_courses)
        student3.payment_plan = PaymentPlan("TRIMESTRAL", student3.total_courses)

    initialize_sample_data(new_manager)

    # persist new manager immediately to avoid losing reset
    save_manager(new_manager)

    print("All data reset to default sample students, teachers, and courses.")
    return new_manager


# -------------------------
# Main menu
# -------------------------
def main():
    """
    Main menu delegating to all submenus.
    Defensive: validates input, handles back/exit, updates manager if reset occurs.
    """
    global manager

    while True:
        print("\n=== Dance School Main Menu ===")
        print("Enter 'b' at any time to go back.")
        print("1. Student Management")
        print("2. Courses Management")
        print("3. Teacher Management")
        print("4. Payment Management")
        print("5. Email Management")
        print("6. Reset all data")
        print("0. Exit")

        choice = get_menu_choice("Choice", ["0", "1", "2", "3", "4", "5", "6"])
        if choice is None:
            break

        if choice == "1":
            student_menu(manager)
        elif choice == "2":
            courses_menu(manager)
        elif choice == "3":
            teacher_menu(manager)
        elif choice == "4":
            payment_menu(manager)
        elif choice == "5":
            email_menu(manager)
        elif choice == "6":
            new_manager = reset_all_data()
            if new_manager:
                manager = new_manager
        elif choice == "0":
            break


# -------------------------
# Run program
# -------------------------
if __name__ == "__main__":
    try:
        main()
    finally:
        save_manager(manager)  # Ensure data persists on exit
