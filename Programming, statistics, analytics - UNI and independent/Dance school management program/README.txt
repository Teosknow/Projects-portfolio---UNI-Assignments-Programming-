# Dance School Management System

## Overview

This is a **console-based Python application** for managing a dance school. It allows administrators to manage students, teachers, courses, payments, and emails efficiently. The system includes features for tracking enrollments, assigning teachers and students to courses, handling payment plans, and generating automated email text.

---

## Features brief overview

### Student Management

* Add, remove, and view students.
* Enroll or disenroll students in courses.
* View students by course.

### Teacher Management

* Add and remove teachers.
* Assign teachers to courses.
* View teachers and their courses.

### Course Management

* Add and remove courses.
* View the list of all courses.

### Payment Management

* Assign payment plans (`YEARLY` or `TRIMESTRAL`) to students.
* Update installment status (PAID/DUE) and track payments.
* Generate summary tables for all students and unpaid installments.

### Email Management

* Generate welcome, reminder, and thank-you emails for students.
* Track email sending status.
* Identify pending emails for students.

### Data Management

* Persistent storage ensures data is saved when exiting the program.

Each feature has also summarising tables.

---

## Installation

Open the console and:

1. Clone the repository:

   ```bash
   cd <repository_folder>
   ```
2. Ensure Python 3.10+ is installed.

3. Install required dependencies (if any; e.g., `tabulate` for tables):

   ```bash
   pip install tabulate
   ```

---

## Usage

1. Run the main script inside the console:

   ```bash
   python main.py
   ```

2. Use the console menus to navigate:

   * **Student Management**: Add/remove/enroll/disenroll students.
   * **Courses Management**: Add/remove/list courses.
   * **Teacher Management**: Add/remove/assign teachers.
   * **Payment Management**: Manage payment plans and installment status.
   * **Email Management**: Generate and track emails for students.
   * **Reset All Data**: Reset the system to sample data.

3. Enter `b` at any input prompt to go back to the previous menu.

---

## Code Structure

* `person.py`: Base class `Person` for students and teachers.
* `student.py`: `Student` class with course enrollment and payment tracking.
* `teacher.py`: `Teacher` class with course assignment.
* `course.py`: `Course` class for managing course info and students.
* `payment.py`: `PaymentPlan` and installment handling.
* `emails.py`: Templates for welcome, reminder, and thank-you emails.
* `school_manager.py`: `SchoolManager` class orchestrating all operations.
* `main.py`: Entry point of the application and console menus for navigating the system.
* `utils.py`: Define helpers functions.
* `storage.py`: Sets up saving mechanism.

---