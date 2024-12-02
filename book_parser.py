import re


class BookParser:
    def __init__(self, page):
        try:
            params = {}

            obj_page = page.find('article', {'class': 'product_page'})
            obj_main = obj_page.find('div', {'class': 'product_main'})
            if obj_page.find('h2', string='Product Information').parent:
                table_descr = obj_page.find('h2', string='Product Information').parent.findNext('table')
                tbl = table_descr.findAll(lambda tag: tag.name == 'tr')

                for row in tbl:
                    params[row.th.text] = row.td.text

            self.title = obj_main.h1.text
            if obj_page.find('div', {'id': 'product_description'}):
                self.description = obj_page.find('div', {'id': 'product_description'}).findNext('p').text.replace('"','""')
            else:
                self.description = ''

            # Определяем рейтинг
            rating_obj = obj_page.find('p', {'class': 'star-rating'})["class"]
            rating_obj.remove('star-rating')
            units = [
                "zero", "one", "two", "three", "four", "five"
            ]
            self.rating = units.index(rating_obj[0].lower())

            # Кол-во книг на продажу
            self.count_remain = 0
            count_remain_obj = params.get('Availability')
            if " available" in count_remain_obj:
                self.count_remain = re.findall(r'\b\d+\b', count_remain_obj)[0]

            # Доп. параметры из таблицы
            self.price = params.get('Price (incl. tax)').replace('Â£', "")
            self.upc = params.get('UPC')
            self.product_type = params.get('Product Type')
            self.count_review = params.get('Number of reviews')
        except Exception as e:
            print(f'При обработке книги возникла ошибка: {e}')

    def getObj(self):
        return [self.upc, self.title, self.price, self.rating, self.count_review, self.product_type, self.description]

    # Отображение информации по книге
    def display_info(self):
        print(
            f"Title: {self.title} \nPrice: {self.price} "
            f"\nRating: {self.rating} \nUpc: {self.upc} "
            f"\nProduct Type: {self.product_type} \nDescription: {self.description} "
            f"\nCount Remain: {self.count_remain} \nCount Review: {self.count_review}")