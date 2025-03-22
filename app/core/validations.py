import re

PASSWORD_MIN_LENGTH = 8
FULL_NAME_PATTERN = re.compile(r"^[a-zA-Zа-яА-Я]+(?: [a-zA-Zа-яА-Я]+)*$")
PHONE_NUMBER_PATTERN = re.compile(r'^\+998\d{9}$')
USERNAME_VALIDATOR = re.compile(r"^[A-Za-z][A-Za-z0-9_]{3,29}$")