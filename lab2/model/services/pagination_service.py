class PaginationService:

    def __init__(self, data, page_size=10):
        self.data = data
        self.page_size = page_size
        self.current_page = 1

    def set_data(self, data):
        self.data = data
        self.current_page = 1

    def set_page_size(self, size):
        self.page_size = size
        self.current_page = 1

    def total_items(self):
        return len(self.data)

    def total_pages(self):
        if not self.data:
            return 1
        return (len(self.data) + self.page_size - 1) // self.page_size

    def get_page_data(self):
        start = (self.current_page - 1) * self.page_size
        end = start + self.page_size
        return self.data[start:end]

    def next(self):
        if self.current_page < self.total_pages():
            self.current_page += 1

    def prev(self):
        if self.current_page > 1:
            self.current_page -= 1

    def first(self):
        self.current_page = 1

    def last(self):
        self.current_page = self.total_pages()