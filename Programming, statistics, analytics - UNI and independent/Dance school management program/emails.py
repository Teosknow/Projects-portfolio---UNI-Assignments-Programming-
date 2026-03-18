from typing import List
from datetime import date


# -------------------------
# Welcome Email Template
# -------------------------
def welcome_email(
    name: str,
    surname: str,
    courses: List[str],
    plan_type: str,
    amounts_dates: List[str],
    school_name: str,
    contact_info: str,
) -> str:
    """
    Generates a welcome email for a new student, including their enrolled courses
    and payment plan details.

    Args:
        name: Student's first name.
        surname: Student's surname.
        courses: List of course names the student is enrolled in.
        plan_type: Payment plan type (e.g., 'YEARLY', 'TRIMESTRAL').
        amounts_dates: List of strings with installment amounts and due dates.
        school_name: Name of the dance school.
        contact_info: Contact details (email, phone).

    Returns:
        Formatted email string.

    Notes:
        - Lists all courses and payment installments.
        - Reminds that changes after first payment may not be allowed.
    """
    course_list = ", ".join(courses)
    amounts_text = "\n".join(amounts_dates)
    return f"""Subject: Welcome to {school_name} – Payment Plan Confirmation
Dear {name} {surname},

Welcome to our dance school! We are thrilled to have you join our community of dancers.

This email is to confirm your enrollment and payment plan. Please review the details below:

Course(s) enrolled: {course_list}

Selected payment plan: {plan_type}

Amounts due and schedule:
{amounts_text}

Once the first installment is made, changes to the payment plan or course selection are generally not allowed to ensure smooth administration. If you need to make adjustments before that first payment, please contact us as soon as possible.

Kindly reply to confirm your enrollment. If you have any questions, we’re here to help.

We look forward to seeing you in class and hope you enjoy every step of your dance journey!

Warm regards,
{school_name}
{contact_info}
"""


# -------------------------
# Reminder Email Template
# -------------------------
def reminder_email(
    name: str,
    surname: str,
    amount: str,
    due_date: date,
    school_name: str,
    contact_info: str,
) -> str:
    """
    Generates a reminder email for a student installment that is due.

    Args:
        name: Student's first name.
        surname: Student's surname.
        amount: Amount due (as string with currency).
        due_date: Date when payment is due.
        school_name: Name of the dance school.
        contact_info: Contact details (email, phone).

    Returns:
        Formatted reminder email string.

    Notes:
        - Only generate this email for installments that are not yet paid.
        - Provides clear due date and amount information.
    """
    return f"""Subject: Reminder: Upcoming Payment Due
Dear {name} {surname},

This is a kind reminder that your next payment for your dance school enrollment is due soon.

Amount due: {amount}

Due date: {due_date.strftime("%Y-%m-%d")}

If you have any questions or need assistance, please do not hesitate to contact us.

Thank you for your attention, and we look forward to seeing you in class!

Warm regards,
{school_name}
{contact_info}
"""


# -------------------------
# Thank You Email Template
# -------------------------
def thank_you_email(
    name: str,
    surname: str,
    paid_installment: "Installment",  # The installment that was just paid
    remaining_installments: list["Installment"],  # All remaining unpaid installments
    school_name: str,
    contact_info: str,
) -> str:
    """
    Generates a thank-you email confirming receipt of a payment, with clear details
    for yearly or trimestral plans.

    Args:
        name: Student's first name.
        surname: Student's surname.
        paid_installment: The installment that was just paid.
        remaining_installments: List of unpaid Installment objects after the payment.
        school_name: Name of the dance school.
        contact_info: Contact details (email, phone).

    Returns:
        Formatted thank-you email string.

    Notes:
        - Correctly handles trimestral plans: shows next installments individually.
        - Payment date is taken from the paid_installment.paid_date.
    """
    payment_date = paid_installment.paid_date or date.today()
    amount_paid = f"{paid_installment.amount:.2f} €"

    # Build remaining installments text
    remaining_text = ""
    if remaining_installments:
        remaining_lines = []
        for idx, inst in enumerate(remaining_installments, start=1):
            remaining_lines.append(
                f"{idx}^ Amount: {inst.amount:.2f} €, Due: {inst.due_date.strftime('%Y-%m-%d')}"
            )
        remaining_text = (
            "\nFollowing installments remain:\n" + "\n".join(remaining_lines) + "\n"
        )

    return f"""Subject: Payment Received – Thank You!
Dear {name} {surname},

We have received your recent payment. Thank you!

Amount paid: {amount_paid}

Payment date: {payment_date.strftime("%Y-%m-%d")}
{remaining_text}If you have any questions or need clarification regarding your payment plan, please feel free to reach out to us.

We appreciate your prompt payment and look forward to seeing you in class!

Warm regards,
{school_name}
{contact_info}
"""
