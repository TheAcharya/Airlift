import re

def guess_data_type(string):

  # Match the string against a regular expression for a number.
  if re.match(r"^\d+\.?\d*$", string):
    return "number"

  # Match the string against a regular expression for a date.
  if re.match(r"^\d{4}-\d{2}-\d{2}$", string):
    return "date"

  # Match the string against a regular expression for an email address.
  if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", string):
    return "email"
  
  if re.match(r"^(?i)(true|false|True|False)$",string):
    return "bool"
  
  # Otherwise, return "unknown".
  return "unknown"