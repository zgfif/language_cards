# this class is used to retrieve the item from the list
class NextListItem:
    def __init__(self, items=None, current_item=None):
        self.items = items
        self.current_item = current_item

    def calculate(self):
        if (not self.current_item or not self.items or not self.is_item_in_list() or
                self.last_item() == self.current_item):
            return None
        if self.current_item == self.last_item():
            return self.items[0]
        else:
            next_index = self.index_of_current_item() + 1
            return self.items[next_index]

    def first_item(self):
        return self.items[0]

    def last_item(self):
        return self.items[-1]

    def is_item_in_list(self):
        return self.current_item in self.items

    def index_of_current_item(self):
        return self.items.index(self.current_item)
