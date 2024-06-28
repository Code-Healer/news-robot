import uuid
import utils

class News:
    def __init__(self):
        self.title = None
        self.description = None
        self.post_datetime = None
        self.img_file_name = None
        self.img_link = None
        self.have_money_values = None
        self.count_of_search_phrase = None
        self._code = None

    @property
    def code(self):
        self._code = self._code or str(uuid.uuid4())
        return self._code

    def get_str_datetime(self):
        if self.post_datetime:
            return self.post_datetime.strftime("%Y-%m-%d %H:%M:%S")

        return None

    def get_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "post_datetime": self.get_str_datetime(),
            "img_file_name": self.img_file_name,
            "have_money_values": self.have_money_values,
            "count_of_search_phrase": self.count_of_search_phrase,
        }

    def have_image(self):
        return self.img_link is not None        


    def __repr__(self):
        return f"NewsData(code='{self.code}', title='{self.title})'"
