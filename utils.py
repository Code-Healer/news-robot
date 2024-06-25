from RPA.HTTP import HTTP
from RPA.Excel.Files import Files

def download_image(url: str, filename: str):
    http = HTTP()
    http.download(url, f'output/images/{filename}', overwrite=True)

def save_dict_in_excel(data: dict, filename: str):
    excel = Files()    
    excel.create_workbook(f"output/{filename}.xlsx")
    
    headers = list(data[0].keys())
    excel.append_rows_to_worksheet([headers])
    
    rows = [list(entry.values()) for entry in data]
    excel.append_rows_to_worksheet(rows)
    
    excel.save_workbook()
    excel.close_workbook()