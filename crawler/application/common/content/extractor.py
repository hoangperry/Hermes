import re
from datetime import datetime
import crawler.application.common.helpers.logger as logger
import crawler.application.common.content.regex as regex
from crawler.application.common.helpers.converter import to_float


def normalize_phone(phone):
    """
    Convert phone with 11 digits to 10 digits or normalize phone prefix
    Example java code
        phone = phone.replaceAll("\\D+", "");

        phone = phone.replaceAll("(^84)", "0");

        if (phone.charAt(0) != '0') {
            return null;
        }

        // init hash table with keys contain phone prefix and value are replacements
        Map<String, String> phoneMaps = new HashMap<String, String>(){{
            // mobiphone
            put("0120", "070");
            put("0121", "079");
            put("0122", "077");
            put("0126", "076");
            put("0128", "078");
            // vinaphone
            put("0123", "083");
            put("0124", "084");
            put("0125", "085");
            put("0127", "081");
            put("0129", "082");
            // viettel
            put("0162", "032");
            put("0163", "033");
            put("0164", "034");
            put("0165", "035");
            put("0166", "036");
            put("0167", "037");
            put("0168", "038");
            put("0169", "039");
            // vietnam mobile
            put("0186", "056");
            put("0188", "058");
            // gmobile
            put("0199", "059");
        }};

        // get prefix and replaced value
        String prefix = phone.substring(0, 4);
        String replaceValue = phoneMaps.get(prefix);

        if (null != replaceValue) {
            // begin with prefix
            phone = phone.replaceAll("(^" + prefix + ")", replaceValue);
        }

        if (phone.length() != 10) {
            return null;
        } else {
            return phone;
        }
    :param phone:
    :return:
    """
    # Remove anthing is not degits
    phone = re.sub(r"\D+", "", phone)
    phone = re.sub(r"(^[+]?84)", "0", phone)

    if phone[0] != "0":
        # print("Not start by 0")
        return None

    # Init hash table with keys contain phone prefix and value are replacements
    prefix_dict = {}
    # mobiphone
    prefix_dict["0120"] = "070"
    prefix_dict["0121"] = "079"
    prefix_dict["0122"] = "077"
    prefix_dict["0126"] = "076"
    prefix_dict["0128"] = "078"
    # vinaphone
    prefix_dict["0123"] = "083"
    prefix_dict["0124"] = "084"
    prefix_dict["0125"] = "085"
    prefix_dict["0127"] = "081"
    prefix_dict["0129"] = "082"
    # viettel
    prefix_dict["0162"] = "032"
    prefix_dict["0163"] = "033"
    prefix_dict["0164"] = "034"
    prefix_dict["0165"] = "035"
    prefix_dict["0166"] = "036"
    prefix_dict["0167"] = "037"
    prefix_dict["0168"] = "038"
    prefix_dict["0169"] = "039"
    # vietnam mobile
    prefix_dict["0186"] = "056"
    prefix_dict["0188"] = "058"
    # gmobile
    prefix_dict["0199"] = "059"

    # get prefix and replaced value
    prefix = phone[:4]
    if prefix in prefix_dict:
        phone = re.sub(prefix[:4], prefix_dict[prefix], phone)

    # Final check
    if len(phone) != 10:
        return None

    return phone


def get_phones(text):
    """
    * Lay so dien thoai tu noi dung bai viet
    * Vi du:
    * this is phone  +8432908-249-265  tin chính chủ
    * duy nhất va
    * Lien he: 0764.87.838 hoac 01212101293
    * <p>
    * => 843290249265, 076487838, 01212101293
    :param text:
    :return:
    """
    if text is None:
        return None
    else:
        phones = set()
        pattern = re.compile(regex.PHONE_PATTERN)
        for matcher in re.finditer(pattern, text):
            # normalize and append to list
            phones.add(normalize_phone(matcher.group(0)))

        if len(phones) == 0:
            return None
        return list(phones)


def get_emails(text):
    """
    Get email from text
    :param text:
    :return:
    """
    if text is None:
        return None
    else:
        emails = []
        pattern = re.compile(regex.EMAIL_PATTERN)
        for matcher in re.finditer(pattern, text):
            emails.append(matcher.group(0))

        if len(emails) == 0:
            return None
        return emails


def get_dates(text):
    """
    Get date from text
    Return list dates
    => [21/2/2002, 11/23/2020]
    :param text:
    :return:
    """
    if text is None:
        return None
    else:
        dates = []
        pattern = re.compile(regex.DATE_PATTERN)
        for matcher in re.finditer(pattern, text):
            try:
                dates.append(datetime(year=int(matcher.group(3)),
                                      month=int(matcher.group(2)),
                                      day=int(matcher.group(1))))
            except Exception as ex:
                logger.error_log.exception(str(ex))
                dates.append(datetime.now())

        if len(dates) == 0:
            return None
        return dates


def get_numbers(text):
    """
    Get numbers from text
    ex: this is 1 text 2 text
    => 12
    :param text:
    :return:
    """
    if text is None:
        return None
    else:
        numbers = re.sub(r'[^\d]+', '', text)
        if bool(numbers):
            return int(numbers)
        else:
            return None


def get_salary(text: str):
    """
    Get (min, max, unit) of salary from text
    :param text:
    :return:
    """
    if text is None:
        return None, None, None
    else:
        try:
            text = text.replace(',', '').replace('.', '')
            # pattern = re.compile(regex.SALARY_PATTERN)
            matcher = re.search(regex.SALARY_PATTERN, text)
            min_salary = matcher.group(2)
            max_salary = matcher.group(4)

            if min_salary is not None:
                min_salary = to_float(min_salary)
                if min_salary > 10000:
                    min_salary = min_salary / 1000000
            if max_salary is not None:
                max_salary = to_float(max_salary)
                if max_salary > 10000:
                    max_salary = max_salary / 1000000

            return min_salary, max_salary, None
        except Exception:
            return None, None, None


def get_price(text, extended=False):
    """
    lay gia tien tu van ban
    Vi du: 3 tỷ 380 triệu
    * => 3.380
    * Vi du: 3.5 tỷ 380 triệu
    * => 3.880
    * Vi du: 3,5 tỷ 380 triệu
    * => 3.880
    * <p>
    * Test method:
    * 2 tỷ 282 triệu dong => 2.282
    * 2.2 tỷ 282 triệu dong => 2.482
    * 2.222 tỷ 282 triệu dong  => 2.504
    * 22 tỷ 2.282 triệu dong => 22.002282
    * 1 triệu => 0.001
    :param text:
    :param extended:
    :return:
    """
    if text is None:
        return None

    # else, extract from text
    price = 0
    text = text.lower()

    # first, search billion values
    matcher = re.search(regex.RE_PRICE_BILLION, text)
    if matcher:
        str_price = re.sub('[^0-9\.\,]+', '', matcher.group(0)).replace(',', '.')
        price = to_float(str_price)

    # then, find million values
    matcher = re.search(regex.RE_PRICE_MILLION, text)
    if matcher:
        try:
            str_price = re.sub('[^0-9\.\,]+', '', matcher.group(0)).replace(',', '.')
            price_in_million = to_float(str_price)
            # convert to billion
            price = price + price_in_million / 1000
        except Exception as ex:
            # logger.error_log.exception(str(ex))
            # logger.error_log.error(str_price)
            pass

    if price == 0 and extended:
        # search price
        matcher = re.search("([\d{1}(.,)?\d{1}]+)\s?((tri[ệe]u)|(t[ỷỉiy]))?", text)
        try:
            str_price = re.sub('[^0-9\.\,]+', '', matcher.group(0)).replace(',', '.')
            price = to_float(str_price)
            if price < 100000:
                pass
            else:
                price = price / 1.0E9

        except Exception as ex:
            # logger.error_log.exception(str(ex))
            # logger.error_log.error(str_price)
            pass

    return None if price == 0 else price


def get_width_length(text):
    """
    * methods
    * lay chieu ngang, chieu dai tu noi dung bai viet
    * input: noi dung bai viet (String content)
    * chieu_ngang, chieu_dai as array
    * vi du 1
    * Ban nha mat tien 4x12 m duong Dien Bien Phu
    * => {4, 12}
    * Ban nha mat tien 4,232*12 m duong Dien Bien Phu
    * => {4.232, 12}
    * call:
    * String[] values = ContentUtils.getChieuNgangChieuDai(text);
    * String chieu_ngang = values[0];
    * String chieu_dai = values[1];
    *
    :param text:
    :return:
    """
    if text is None:
        return None, None

    # else, extract from text
    matcher = re.search(regex.RE_WIDTH_LENGTH, text)
    if matcher:
        width = matcher.group(1).replace(",", ".")
        length = matcher.group(3).replace(",", ".")
        return to_float(width), to_float(length)
    else:
        return None, None


def get_int_patterns(text, type='floors'):
    if text is None:
        return None

    # else, extract from text
    if type == 'floors':
        matcher = re.search(regex.RE_FLOORS, text)
    elif type == 'bedrooms':
        matcher = re.search(regex.RE_BEDROOMS, text)
    elif type == 'bathrooms':
        matcher = re.search(regex.RE_BATHROOMS, text)
    else:
        matcher = None

    if matcher:
        int_val = int(matcher.group(1))
        return int_val
    else:
        return None


def get_direction(text: str):
    """
    Get direction from input text : mat tien, hem, null
    mat tien = 'h-front'
    hem = 'h-alley'
    null = khong xac dinh
    :param text:
    :return:
    """
    if text is None:
        return None
    else:
        text = text.lower()

        if "hẻm" in text or 'hem' in text:
            return "h-alley"
        elif "mặt tiền" in text or 'mat tien' in text:
            return "h-front"
        else:
            return None
