import re

def validate_usn(usn: str):

  pattern = r"^[1-4][A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{3}$"

  usn = usn.upper()

  return re.match(pattern, usn)

