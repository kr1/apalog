"this module contains the patterns used by apalog"

HTTP_STATUS_TEMPLATE = 'HTTP/1.[10]" {}'
HTTP_STATUS_GROUP = 'HTTP/1.[10]" (...)'

DATE_PATTERN = "[0-9]{2}/[a-zA-Z]{3}/[0-9]{4}"
RESPONSE_SIZE_QUANTIFIER_TEMPLATE = 'HTTP/1.[10]" [0-9]{{3}} [0-9]*([0-9]{}) '
RESPONSE_SIZE = 'HTTP/1.[10]" [0-9]{3} ([0-9]*) '
