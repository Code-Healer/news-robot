class News:
    def __init__(self):
        self.title = None
        self.description = None
        self.post_datetime = None
        self.img_file_name = None
        self.img_link = None

    @property
    def code(self):
        return '-'.join([
        self.post_datetime.strftime("%Y%m%d%H%M%S"),
        self.title[0:11].replace(" ", "_")
    ])

    def get_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "post_datetime": self.post_datetime,
            "img_file_name": self.img_file_name,
        }

    def have_image(self):
        return self.img_link is not None

    def __repr__(self):
        return f"NewsData(code='{self.code}', title='{self.title})'"