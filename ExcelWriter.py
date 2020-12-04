import xlsxwriter

class WriteExcel:
    Worksheet = None

    def __init__(self):
        self.Workbook = xlsxwriter.Workbook('Komponenty.xlsx')

    def add_sheet(self):
        self.Worksheet = self.Workbook.add_worksheet()

    def add_data(self, row, column):
        return None

    def fill_column_in_loop(self, row, column, value):
        self.Worksheet.write(str(column) + str(row), value)
        return row + 1

    def close_workbook(self):
        self.Workbook.close()

    def change_cell_size(self, cell, size):
        self.Worksheet.set_column(cell, size)

