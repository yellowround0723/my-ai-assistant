import os
import poplib
import ssl

from email import policy
from email.header import decode_header, make_header
from email.parser import BytesParser


def decode_text(value):
    if not value:
        return ""
    return str(make_header(decode_header(str(value))))


def fetch_company_emails(limit=10):
    username = os.environ.get("COMPANY_EMAIL_USER")
    password = os.environ.get("COMPANY_EMAIL_PASSWORD")
    host = os.environ.get("COMPANY_POP3_HOST")
    port = int(os.environ.get("COMPANY_POP3_PORT", "995"))

    if not username or not password or not host:
        raise ValueError("Company email settings are missing")

    connection = poplib.POP3_SSL(
        host,
        port,
        timeout=30,
        context=ssl.create_default_context()
    )

    try:
        connection.user(username)
        connection.pass_(password)

        count, _ = connection.stat()
        messages = []

        for number in range(count, max(count - limit, 0), -1):
            _, lines, _ = connection.retr(number)

            raw_message = b"\r\n".join(lines)

            message = BytesParser(
                policy=policy.default
            ).parsebytes(raw_message)

            messages.append({
                "date": str(message.get("Date", "")),
                "sender": decode_text(message.get("From")),
                "subject": decode_text(message.get("Subject"))
            })

        return messages

    finally:
        try:
            connection.quit()
        except Exception:
            connection.close()


if __name__ == "__main__":
    try:
        emails = fetch_company_emails()

        print("Company email connection successful")
        print(f"Emails retrieved: {len(emails)}")

    except Exception as error:
        print(
            "Company email connection failed:",
            type(error).__name__
        )
