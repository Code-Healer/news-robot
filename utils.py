from datetime import datetime
import re

from RPA.HTTP import HTTP
from RPA.Excel.Files import Files


def download_image(url: str, filename: str):
    http = HTTP()
    http.download(url, f'output/{filename}', overwrite=True)

def save_dict_in_excel(data: dict, filename: str):
    excel = Files()    
    excel.create_workbook(f"output/{filename}.xlsx")
    
    headers = list(data[0].keys())
    excel.append_rows_to_worksheet([headers])
    
    rows = [list(entry.values()) for entry in data]
    excel.append_rows_to_worksheet(rows)
    
    excel.save_workbook()
    excel.close_workbook()

def get_period(months: int):
    today = datetime.today()
    end_date = today

    start_year = today.year
    start_month = today.month - (months - 1)

    while start_month <= 0:
        start_month += 12
        start_year -= 1

    start_date = datetime(start_year, start_month, 1)

    return (start_date, end_date)

def is_date_within_period(date_to_check: datetime, period: tuple) -> bool:
    start_date, end_date = period
    return start_date <= date_to_check <= end_date


def check_money_values(text):
        patterns = [
            r'\$\d{1,3}(,\d{3})*(\.\d{2})?',
            r'\b\d{1,3}(,\d{3})*(\.\d{2})? dollars\b',
            r'\b\d{1,3}(,\d{3})*(\.\d{2})? USD\b'
        ]

        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False