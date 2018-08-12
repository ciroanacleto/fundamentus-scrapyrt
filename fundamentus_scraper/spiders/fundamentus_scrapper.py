# coding: utf-8
import scrapy
from unicodedata import normalize

class PaperScrapper(scrapy.Spider):
    name = "fundamentus"

    def parse(self, response):
        tables = []
        for table in response.css('table'):
            tables.append(self.retrieve_table(table))

        tables[0] = self.extract_table_info(tables[0] + tables[1])
        tables[2] = self.extract_table_info(tables[2], 1)
        tables[3] = self.extract_table_info(tables[3], 2)
        tables[4] = self.extract_table_info(tables[4], 3)

        yield {
            'info': tables[0],
            'oscilations': tables[2]['oscilations'],
            'fundamentals': tables[2]['fundamentals'],
            'patrimonial_balance_data': tables[3],
            'demonstrative_results_data': tables[4]
        }

    def extract_table_info(self, table, extraction_type=0):
        company_info = {}

        if extraction_type == 0:
            for row in table:
                for j in range(0, len(row), 2):
                    if j % 2 == 0:
                        attr = self.transform_string(row[j])
                        company_info[attr] = row[j+1] 

            return company_info

        elif extraction_type == 1:
            table = table[1:]
            company_info = {'oscilations': {}, 'fundamentals': {}}

            for row in table:
                attr = self.transform_string(row[0])
                if table.index(row) == len(table) - 1:
                    company_info['fundamentals'][attr] = row[1].replace('\n', '').strip()
                else:
                    company_info['oscilations'][attr] = row[1]
                    row = row[2:]

                    for j in range(0, len(row), 2):
                        if j % 2 == 0:
                            attr = self.transform_string(row[j])
                            company_info['fundamentals'][attr] = row[j+1].replace('\n', '').strip()

            return company_info

        elif extraction_type == 2:
            table = table[1:]
            for row in table:
                for j in range(0, len(row), 2):
                    if j % 2 == 0:
                        attr = self.transform_string(row[j])
                        company_info[attr] = row[j+1] 
            return company_info

        elif extraction_type == 3:
            table = table[2:]
            company_info = {'last_year': {}, 'last_quarter': {}}

            for row in table:
                attr1 = self.transform_string(row[0])
                attr2 = self.transform_string(row[2])
                company_info['last_year'][attr1] = row[1]
                company_info['last_quarter'][attr2] = row[3]

            return company_info


    def transform_string(self, string):
        string = normalize('NFKD', string).encode('ASCII', 'ignore').decode('ASCII')
        string = string.replace('$', '')
        string = string.replace('.', '')
        string = string.replace(' ', '_')
        string = string.replace('_/_', '/')
        string = string.replace('__', '_')
        string = string.replace('/_', '/')
        string = string.replace('(', '')
        string = string.replace(')', '')
        string = string.replace('/', '_')
        string = string.lower()

        return string


    def retrieve_row(self, row):
        row = list(filter(lambda a: a != '?', row.xpath('td//text()').extract()))
        return row

    def retrieve_table(self, table):
        res_rows = []
        rows = table.css('tr')
        for row in rows:
            res_rows.append(self.retrieve_row(row))

        return res_rows