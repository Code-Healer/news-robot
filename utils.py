from RPA.HTTP import HTTP

def download_image(url, filename):
    http = HTTP()
    http.download(url, f'output/images/{filename}', overwrite=True)