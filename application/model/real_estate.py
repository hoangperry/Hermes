class Property:

    title: str = None
    price: float = None
    house_type: str = None
    floors: int = None
    description: str = None
    total_area: float = None
    # phap ly
    legal_status: str = None
    total_area_length: float = None
    total_area_width: float = None
    # Vị trí: Mặt tiền (hfront), trong hẻm (halley),...
    location: str = None
    # so nha
    address_number: str = None
    street_name: str = None
    ward_name: str = None
    district_name: str = None
    province_name: str = None
    # lo gioi
    area_ilegal_recognized: float = None
    bathrooms = None
    # huong: dnorth, dsouth,...
    direction: str = None
    bedrooms: int = None
    # Contact
    contact_email: str = None
    contact_address: str = None
    contact_name: str = None
    contact_phone: str = None
    contact_phone_1: str = None
    contact_phone_2: str = None
    source: str = None
    # sha1 encoding
    url_hash: str = None
    domain: str = None
    # House Info
    ads_type: str = None
    # address
    address: str = None
    street_id: str = None
    ward_id: str = None
    district_id: str = None
    province_id: str = None

    # thong tin them sau yeu cau
    # thong tin dien tich
    construction_area: float = None
    # ten du an
    project_name: str = None
    project_id: str = None
    # tang so
    in_floor_th: int = None
    posted_date: str = None
    contact_table: str = None
    description_table: str = None
    # add prefix
    pre_direction = pre_legal_status = pre_location = pre_total_area = pre_total_area_width = None
    pre_total_area_length = pre_construction_area = pre_area_ilegal_recognized = None
    pre_floors = pre_bedrooms = pre_bathrooms = None
    pre_contact_name = pre_contact_phone = pre_contact_address = pre_contact_email = None
    pre_property_address = None

    def set_dict(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def optimize_dict(self):
        ob_dict = dict()
        for key, value in self.__dict__.items():
            if not key.startswith("pre_") and not key.endswith("_table"):
                ob_dict[key] = value

        return ob_dict

    def is_valid(self):
        if self.title is not None:
            return True
