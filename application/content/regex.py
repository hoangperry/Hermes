EMAIL_PATTERN = r'\S+@\S+\.[a-zA-Z]{2,}'
PHONE_PATTERN = r'(0[1-9]{1,2}|\+?84[1-9]{1,2})[ \d.-]{5,9}\d'
FLOAT_PATTERN = ''

# group 0 present complete datetime 12/2/1992,
# group 1, 2, 3 => day, month, year
DATE_PATTERN = r'(0?[1-9]|[1-2][0-9]|3[01])[/-](0?[1-9]|1[0-2])[/-](\d{4})'

SALARY_PATTERN = r'(luong|lương)?\s?(\d+)(\s?tri[ệe]u|tr)?\s?-?\s?(\d+)?(\s?tri[ệe]u|tr)?\s?'

# region real estate
RE_FLOORS = r'(\d+) ?(lầu|lau|tầng|tang)'
RE_BEDROOMS = r'(\d+) ?(phòng ngủ|phong ngu|p ngủ|p ngu)'
RE_BATHROOMS = r'(\d+) ?(phòng tắm|phong tam|p tắm|p tam|toilet|toilets|nhà vệ sinh|nha ve sinh|WC|wc)'
RE_WIDTH_LENGTH = r'(\d+(,\d+|\.\d+)?) ?m? ?[x|X|*] ?(\d+(,\d+|\.\d+)?) ?m?'
RE_PRICE_BILLION = r'([\d{1}(.,)?\d{1}]+)\s?t[ỷỉiy]'
RE_PRICE_MILLION = r'([\d{1}(.,)?\d{1}]+)\s?tri[ệe]u'
RE_PRICE = r'([\d{1}(.,)?\d{1}]+)\s?((tri[ệe]u)|(t[ỷỉiy]))?'
# endregion
