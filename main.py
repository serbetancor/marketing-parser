from scraperStradivarius import StradivariusProductsScraper
from scraperZara import ZaraProductsScraper

def main():
    url_stradivarius = 'https://www.stradivarius.com/es/'
    output_file_path_stradivarius = './data/productsStradivarius.json'

    url_zara = 'https://www.zara.com/es/'
    output_file_zara = './data/productsZara.json'
    
    # scraperStr = StradivariusProductsScraper(url_stradivarius, output_file_path_stradivarius)
    # scraperStr.scrape_and_save_categories()

    scraperZara = ZaraProductsScraper(url_zara, output_file_zara)
    scraperZara.scrape_and_save_categories()

if __name__ == "__main__":
    main()