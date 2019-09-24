from application.common.helpers import logger
from application.common.helpers.converter import dict_to_object, to_float, to_int
from application.config.api_config import APIConfig
from application.model.real_estate import Property
import application.common.content.extractor as extractor
import re
from datetime import datetime
import requests
import simplejson as json


class ContentUtils:
    def __init__(self, content: str):
        self.content = content.lower()

    def get_price(self, prefix):
        pattern = '(' + prefix.lower() + '\s*:?\s*(\d+(\.\d+)?)\s+?(t[ỷỉ]|triệu))'
        matcher = re.search(pattern, self.content)
        if matcher:
            price = to_float(matcher.group(2))
            unit = matcher.group(3).lower()
            if unit == 'tỷ' or unit == 'tỉ':
                pass
            elif unit == 'triệu':
                price = price / 1000
            else:
                self.content = self.content.replace(matcher.group(0), "")

            return price
        else:
            return None

    def get_area(self, prefix):
        pattern = "(" + prefix.lower() + "\s*:?\s*(\d+(\.\d+)?)(\s{0,1}(m[²2])?)?)"
        matcher = re.search(pattern, self.content)
        if matcher:
            area = to_float(matcher.group(2))
            self.content = self.content.replace(matcher.group(0), '')
            return area
        else:
            return None

    def get_width_or_length(self, prefix):
        pattern = "(" + prefix.lower() + "\s*:?\s*(\d+(\.\d+)?)(\s{0,1}m)?)"
        matcher = re.search(pattern, self.content)
        if matcher:
            value = to_float(matcher.group(2))
            self.content = self.content.replace(matcher.group(0), "")
            return value
        else:
            return None

    def get_direction(self, prefix):
        pattern = "(" + prefix.lower() + "\s*:?\s*(tây[ -]nam|đông[ -]bắc|đông[ -]nam|tây[ -]bắc|tây|bắc|nam|đông))"
        matcher = re.search(pattern, self.content)
        if matcher:
            direction = matcher.group(2)
            self.content = self.content.replace(matcher.group(0), "")
            return direction
        else:
            return None

    def get_rooms(self, prefix):
        pattern = "(" + prefix.lower() + "\s*:?\s*(\d+))"
        matcher = re.search(pattern, self.content)
        if matcher:
            rooms = to_int(matcher.group(2))
            self.content = self.content.replace(matcher.group(0), "")
            return rooms
        else:
            return None

    def get_date(self):
        """
        Get date from text
        if date equals "Hôm qua" => yesterday
        if date equals "Hôm nay", "n giờ trước", "n phút trước",... => today
        :return:
        """
        if self.content is not None:
            now = datetime.now()
            if "hôm qua" in self.content:
                return datetime(now.year, now.month - 1, now.day)
            elif "hôm nay" in self.content or re.match(".*\d+.*(phút|giờ|giây) trước.*", self.content):
                return datetime(now.year, now.month, now.day)
            else:
                dates = extractor.get_dates(self.content)
                if dates is not None:
                    return dates[0]
                else:
                    return None
        return None

    def get_email(self):
        """
        Get email from text
        :return:
        """
        emails = extractor.get_emails(self.content)
        if emails is not None:
            return emails[0]
        else:
            return None

    def get_phone(self):
        """
        Get phone from text
        :return:
        """
        phones = extractor.get_phones(self.content)
        if phones is not None:
            return phones[0]
        else:
            return None

    def get_address(self, prefix):
        """
        Get address from text by remove prefix
        :param prefix:
        :return:
        """
        pattern = "(" + prefix.lower() + "\s*:?\s*(" + ".*" + "))"
        matcher = re.search(pattern, self.content)
        if matcher:
            address = matcher.group(2)
            self.content = self.content.replace(matcher.group(0), "")
            return address.title()
        else:
            return None

    def get_name(self, prefix):
        """
        Get name with prefix
        :param prefix:
        :return:
        """
        pattern = prefix.lower() + "\s*:?\s*"
        name = re.sub(pattern, '', self.content)
        name = name.replace(".", "")
        return name.title()


class PropertyNormalizer:

    def __init__(self, prop: Property):
        self.property = prop

    def get_direction(self):
        if self.property.location is None:
            title_direction = extractor.get_direction(self.property.title)
            des_direction = extractor.get_direction(self.property.description)

            # return None if both are none
            if title_direction is None and des_direction is None:
                return None
            else:
                return title_direction if title_direction == des_direction else None
        else:
            return extractor.get_direction(self.property.location)

    def get_bathrooms(self):
        if self.property.bathrooms is None:
            self.property.bathrooms = extractor.get_int_patterns(self.property.description, 'bathrooms')

    def get_bedrooms(self):
        if self.property.bedrooms is None:
            self.property.bedrooms = extractor.get_int_patterns(self.property.description, 'bedrooms')

    def get_area(self):
        if self.property.total_area_width is None or self.property.total_area_length is None:
            width, length = extractor.get_width_length(self.property.description)

            self.property.total_area_width = width
            self.property.total_area_length = length

        if self.property.total_area is not None:
            if self.property.total_area_width is not None and self.property.total_area_length is not None:
                self.property.total_area = self.property.total_area_width * self.property.total_area_length

    def get_floors(self):
        if self.property.floors is None:
            self.property.floors = extractor.get_int_patterns(self.property.description, 'floors')

    def get_price(self):
        if self.property.price is None:
            self.property.price = extractor.get_price(self.property.description)

        if self.property.price is None:
            self.property.price = extractor.get_price(self.property.title)

    def get_phones(self):
        if self.property.contact_phone is None:
            des_phones = extractor.get_phones(self.property.description)
            tit_phones = extractor.get_phones(self.property.title)

            if tit_phones is not None and des_phones is not None:
                phones = list(set(des_phones + tit_phones))
            elif tit_phones is not None or des_phones is not None:
                phones = des_phones if des_phones is not None else tit_phones
            else:
                phones = None
        else:
            phones = extractor.get_phones(self.property.contact_phone)

        # extract phones from contact phone
        if phones is not None:
            if len(phones) == 1:
                self.property.contact_phone_1 = phones[0]
            else:
                self.property.contact_phone_1 = phones[0]
                self.property.contact_phone_2 = phones[1]

    def normalize_property(self):

        if self.property.description is not None:
            self.property.description = re.sub(r"[^\u0000-\uFFFF]", r"\uFFFD", self.property.description)

        if self.property.address_number is not None:
            # normalize address
            self.property.address_number = normalize_address_number(self.property.address_number)

            self.property.address_number = self.property.address_number if self.property.address_number is not None else ''
            if re.match('(^[0-9]+\s?m[2²]?$)', self.property.address_number):
                self.property.address_number = None

            self.property.address_number = self.property.address_number if self.property.address_number is not None else ''
            if re.match('([0-9]+\s?t[ỷỉ])', self.property.address_number):
                self.property.address_number = None

        if self.property.address_number == '':
            self.property.address_number = None

        # normalize huong'
        if self.property.direction is not None:
            direction_lower = self.property.direction.lower()
            direction_lower = re.sub("\W", " ", direction_lower)
            direction_lower = re.sub(" +", " ", direction_lower)
            direction_lower = direction_lower.strip()

            # select case
            if direction_lower == 'dong':
                self.property.direction = "d-east"
            elif direction_lower == 'tay':
                self.property.direction = "d-west"
            elif direction_lower == 'nam':
                self.property.direction = "d-south"
            elif direction_lower == 'bac':
                self.property.direction = "d-north"
            elif direction_lower == 'tay bac':
                self.property.direction = "d-northwest"
            elif direction_lower == 'dong bac':
                self.property.direction = "d-northeast"
            elif direction_lower == 'tay nam':
                self.property.direction = "d-southwest"
            elif direction_lower == 'dong nam':
                self.property.direction = "d-southeast"
            else:
                self.property.direction = None

        # normalize price
        if self.property.price is not None:
            if self.property.price > 1000000:
                self.property.price = self.property.price / 1.0E9

    def extract(self):
        if self.property.title is not None:
            self.property.title = self.property.title[0]

        if self.property.description is not None:
            self.property.description = self.property.description[0]

        if self.property.address is not None:
            self.property.address = self.property.address[0]

        if self.property.price is not None:
            nor_price = extractor.get_price(self.property.price[0], extended=True)
            if nor_price is not None:
                self.property.price = nor_price
            else:
                self.property.price = get_price(self.property.price[0])

        if self.property.posted_date is not None:
            utils = ContentUtils(self.property.posted_date[0])
            self.property.posted_date = utils.get_date()

        if self.property.total_area is not None:
            self.property.total_area = get_area(self.property.total_area[0])

        if self.property.contact_name is not None:
            self.property.contact_name = self.property.contact_name[0]

        if self.property.contact_phone is not None:
            phones = extractor.get_phones(self.property.contact_phone[0])
            if phones is not None:
                self.property.contact_phone = phones[0]

        if self.property.contact_email is not None:
            self.property.contact_email = self.property.contact_email[0]

        # region contacts
        # get contact elementsc
        if self.property.contact_table is not None:
            for row in self.property.contact_table:
                utils = ContentUtils(row)
                if self.property.contact_email is None:
                    self.property.contact_email = utils.get_email()

                if self.property.contact_phone is None:
                    self.property.contact_phone = utils.get_phone()

                if self.property.contact_name is None and self.property.pre_contact_name is not None:
                    self.property.contact_name = utils.get_name(self.property.pre_contact_name)

        # endregion

        # region description
        if self.property.description_table is not None:
            for row in self.property.description_table:
                utils = ContentUtils(row.replace("\n", " "))

                if self.property.address is None and self.property.pre_property_address is not None:
                    self.property.address = utils.get_address(self.property.pre_property_address)

                if self.property.total_area is None and self.property.pre_total_area is not None:
                    self.property.total_area = utils.get_area(self.property.pre_total_area)

                if self.property.total_area_length is None and self.property.pre_total_area_length is not None:
                    self.property.total_area_length = utils.get_width_or_length(self.property.pre_total_area_length)

                if self.property.total_area_width is None and self.property.pre_total_area_width is not None:
                    self.property.total_area_width = utils.get_width_or_length(self.property.pre_total_area_width)

                if self.property.floors is None and self.property.pre_floors is not None:
                    self.property.floors = utils.get_rooms(self.property.pre_floors)

                if self.property.bathrooms is None and self.property.pre_bathrooms is not None:
                    self.property.bathrooms = utils.get_rooms(self.property.pre_bathrooms)

                if self.property.bedrooms is None and self.property.pre_bedrooms is not None:
                    self.property.bedrooms = utils.get_rooms(self.property.pre_bedrooms)

                # huong dong, tay, nam, bac, xxx, xxx, xxx, xxx, xxx
                if self.property.direction is None and self.property.pre_direction is not None:
                    self.property.direction = utils.get_direction(self.property.pre_direction)

        #endregion

    def get_address(self):
        """
        Get address from address, title, description
        Call API
        :return:
        """
        #url = 'api-vietnam-1.newai.vn:0204/rest/api/query/parse-address-multi'
        #headers = {'Content-type': 'application/json'}
        try:
            data = dict()
            data['key'] = APIConfig.PredictAddressFromText.key
            data['address'] = self.property.address
            data['title'] = self.property.title
            data['description'] = self.property.description
            response = requests.post(APIConfig.PredictAddressFromText.url,
                                     data=json.dumps(data),
                                     headers=APIConfig.PredictAddressFromText.headers)

            if response.ok:
                results = response.json()

                dict_results = results

                results = dict_to_object(results)

                if 'province' in dict_results and results.province is not None:
                    # add to property
                    self.property.province_name = results.province.name
                    self.property.province_id = results.province.id

                if 'district' in dict_results and results.district is not None:
                    self.property.district_name = results.district.name
                    self.property.district_id = results.district.id

                if 'ward' in dict_results and results.ward is not None:
                    self.property.ward_name = results.ward.name
                    self.property.ward_id = results.ward.id

                if 'street' in dict_results and results.street is not None:
                    self.property.street_name = results.street.name
                    self.property.street_id = results.street.id

                # add addressnumber
                if 'houseNumber' in dict_results:
                    self.property.address_number = results.houseNumber

                if 'apartment' in dict_results and results.apartment is not None:
                    # and project (apartment)
                    self.property.project_name = results.apartment.name
                    self.property.project_id = results.apartment.id
        except Exception as ex:
            logger.error_log.exception(str(ex))

    def get_ads_type(self):
        """
        Get entity add type based on price or text
        :return:
        """
        if self.property.price is not None:
            if self.property.price > 0.2 or (self.property.title is not None and 'bán' in self.property.title):
                self.property.ads_type = "ad-selling"
            else:
                self.property.ads_type = "ad-leasing"
        else:
            if self.property.title is not None and 'bán' in self.property.title:
                self.property.ads_type = "ad-selling"
            else:
                self.property.ads_type = "ad-leasing"

    def get_house_type(self):
        """
        Get entity house type by calling api
        :return:
        """
        try:
            response = requests.post(url=APIConfig.RealEstateClassifier.url,
                                     data=json.dumps({"text": self.property.title}),
                                     headers=APIConfig.RealEstateClassifier.headers)

            # get response
            # get value of response if request is ok. otherwise set default to tp-house
            if response.ok:
                response = response.json()
                house_type = response['type']
                self.property.house_type = house_type
            else:
                self.property.house_type = "tp-house"
        except Exception as ex:
            logger.error_log.exception(str(ex))
            self.property.house_type = "tp-house"

    def normalize(self):
        try:
            self.extract()
            self.get_house_type()
            self.get_ads_type()
            self.get_direction()
            self.get_bathrooms()
            self.get_bedrooms()
            self.get_area() # not implement
            self.get_floors()
            self.get_price()
            self.get_phones()
            self.get_address()
            self.normalize_property()
        except Exception as ex:
            logger.error_log.exception(str(ex))
        finally:
            return self.property


def get_price(text: str):
    """
        content = content.replace("m2", "");
        content = content.replace("m²", "");
        content = content.replace(",", ".");

        // check price unit
        if (content.contains("tỷ") || content.contains("tỉ")) {
            // replace all characters, dot and commas
            content = content.replaceAll("[^\\d.]+", "");
        } else if (content.contains("triệu")) {
            content = content.replaceAll("[^\\d.]+", "");
            // chuyen sang ty dong
            // convert to billion
            content = String.valueOf(Double.valueOf(content) / 1000);
        } else {
            // default case
            // first check default price unit
            double defaultPrice = UnitConvertUtils.getFloat(
                    content.replaceAll("[^\\d]+", "")
            );

            if (defaultPrice > 1000) {
                defaultPrice = defaultPrice / 1.0E9;
                return defaultPrice;
            }

            // else, skip
            content = content.replaceAll("[^\\d.]+", "");
        }
    :param text:
    :return:
    """
    if text is None:
        return None
    else:
        text = text.replace("m2", '')
        text = text.replace("m²", '')
        text = text.replace(',', '.')
        text = text.lower()
        # check price unit
        if "tỷ" in text or "tỉ" in text:

            # replace all characters, dot and commas
            val = re.sub("[^0-9\.]+", "", text)
            return to_float(val)
        elif "triệu" in text:
            text = re.sub("[^0-9\.]+", "", text)
            # chuyen sang ty dong
            # convert to billion
            val = to_float(text) / 1000
            return val
        else:
            try:
                # default case
                # first check default price unit
                default_price = to_float(re.sub('[^0-9\.]+', '', text))

                if default_price > 1000:
                    return default_price / 1.0E9

                text = re.sub("[^0-9\.]+", '', text)

                return to_float(text)
            except Exception:
                return None


def get_area(text: str):
    text = text.replace('m2', '')
    text = text.replace('m²', '')
    text = text.replace(',', '.')

    text = re.sub('[^0-9\.]+', '', text)

    return to_float(text)


def normalize_address_number(address_number: str):
    """
    /**
     * Normalize address number by using rules
     * 1. Remove first zero number
     * - 01A Nguyen Van Troi => 1A Nguyen Van Troi
     * - 1/020 Phan Dinh Phung => 1/20
     * - A02 => A2
     * 2. To lower case
     * 3. Replace and strip all delimiter symbols
     * @param addressNumber
     * @return
     */
    :param address_number:
    :return:
    """
    replaceNumberPattern = "(\d+)"
    normalizeExtraPattern = "\s*[/-]\s*"

    pattern = re.compile(replaceNumberPattern)
    for matcher in re.finditer(pattern, address_number):
        # find pattern
        find = matcher.group(0)
        replacement = to_int(find)
        address_number = address_number.replace(find, str(replacement), 1)

    address_number = re.sub(normalizeExtraPattern, '/', address_number) # address_number.replaceAll(normalizeExtraPattern, "/")

    return address_number.lower().strip()


