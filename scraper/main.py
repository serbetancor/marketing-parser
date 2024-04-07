from scraperStradivarius import StradivariusProductsScraper
from scraperZara import ZaraProductsScraper
from scraperMango import MangoProductsScraper


def main():
    url_stradivarius = 'https://www.stradivarius.com/es/'
    output_file_path_stradivarius = '../data/productsStradivarius.json'

    # scraperStr = StradivariusProductsScraper(url_stradivarius, output_file_path_stradivarius)
    # scraperStr.scrape_and_save_categories()

    url_zara = 'https://www.zara.com/es/'
    output_file_zara = '../data/productsZara.json'

    # scraperZara = ZaraProductsScraper(url_zara, output_file_zara)
    # scraperZara.scrape_and_save_categories()

    url_mango = 'https://shop.mango.com/es'
    output_file_mango = '../data/productsMango.json'

    scraperMango = MangoProductsScraper(url_mango, output_file_mango)
    scraperMango.scrape_and_save_categories()

if __name__ == "__main__":
    main()