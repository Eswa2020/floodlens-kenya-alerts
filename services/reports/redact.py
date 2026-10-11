"""PII redaction for report text, logs and public outputs.

Covers emails and Kenyan phone numbers (+254 / 254 / 07xx / 01xx forms).
Photos that contain a person are never passed on: the photo reference is
replaced with a privacy marker (faces and homes are personal data under the
Kenya Data Protection Act, 2019).
"""
import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
KENYA_PHONE = re.compile(r"(?<!\d)(?:\+?254|0)[\s-]?[71]\d{2}[\s-]?\d{3}[\s-]?\d{3}(?!\d)")

EMAIL_MARK = "[REDACTED_EMAIL]"
PHONE_MARK = "[REDACTED_PHONE]"
PHOTO_MARK = "[REDACTED_PHOTO:person_present]"


def redact(text: str) -> str:
    if not text:
        return text
    text = EMAIL.sub(EMAIL_MARK, text)
    return KENYA_PHONE.sub(PHONE_MARK, text)


def redact_photo_ref(photo_ref: str | None, has_person: bool) -> str | None:
    if photo_ref and has_person:
        return PHOTO_MARK
    return photo_ref


def contains_pii(text: str) -> bool:
    return bool(text) and bool(EMAIL.search(text) or KENYA_PHONE.search(text))
