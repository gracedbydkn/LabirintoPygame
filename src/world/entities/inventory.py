# src/world/entities/inventory.py

class Inventory:
    def __init__(self, capacity=10):
        self._items = []
        self.capacity = capacity

    def adicionar(self, item):
        if len(self.items) < self.capacity:
            self._items.append(item)
            return True
        return False

    def remover(self, item_type):
        for item in self._items:
            if item.item_type == item_type:
                self._items.remove(item)
                return item
        return None
    
    def tem(self, item_type):
        return any(item.item_type == item_type for item in self._items)

    def listar(self):
        return list(self._items)
    
    def __len__(self):
        return len(self._items)