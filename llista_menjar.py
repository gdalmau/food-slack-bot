# -*- coding: utf-8 -*-


class FoodList(dict):
    def get_llista(self):
        if not self.items():
            return '\n - N/A'
        res = ''
        for food, amount in sorted(self.items()):
            res += '\n - {}: {}'.format(food, amount)
        return res


class FoodManager(object):
    def __init__(self):
        self.lists = {}
    
    def create_list(self, channel, message):
        if channel in self.lists and self.lists[channel]:
            return ("Ja existeix una llista en el canal '{}',"
                    " utilitza la comanda 'done'"
                    " per donar-la per finalitzada").format(channel)
        llista = FoodList()
        self.lists[channel] = (message+'\n', llista)
        return message + llista.get_llista()

    def add_to_list(self, channel, food_message):
        message = food_message.lower()
        if channel not in self.lists or not self.lists[channel]:
            return ("No existeix una llista en aquest canal")
        titol, llista = self.lists[channel]
        if message.lower() not in llista:
            llista[message] = 1
        else:
            llista[message] += 1
        return titol + llista.get_llista()

    def status(self, channel):
        if channel in self.lists and self.lists[channel]:
            return True
        return False


    def end_list(self, channel, message):
        if channel in self.lists and self.lists[channel]:
            titol, llista = self.lists[channel]
            self.lists[channel] = False
            return titol + llista.get_llista()
        return "No controlo cap llista Mort de Gana!"