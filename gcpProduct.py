import requests
from bs4 import BeautifulSoup
import json


def google_product_scraper():
    """
    Scrapes the Google Cloud Platform products page and returns a list of dictionaries containing the product section
    and its corresponding services.

    Returns:
        list: A list of dictionaries containing the product section and its corresponding services.
    """
    url = "https://cloud.google.com/products#section-5"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    heading_elements = soup.find_all(class_="link-card-grid-section cloud-jump-section")

    data = []
    for heading_element in heading_elements:
        heading = heading_element.find(
            class_="cws-headline--headline-3 link-card-grid-module__headline cws-content-block__headline").text.strip()
        services = []
        parent_elements = heading_element.find_all(class_="cws-grid cws-cards cws-cards--compact")

        for parent_element in parent_elements:
            service_elements = parent_element.find_all(class_="cws-card__inner")

            for service_element in service_elements:
                headline = service_element.find(class_="cws-headline cws-headline--headline-5").text.strip()
                description = service_element.find(class_="cws-body").text.strip()
                service = {
                    "ProductName": headline,
                    "Description": description
                }
                services.append(service)

        # Exclude irrelevant heading as this just shows products that are featured.
        if heading not in ["Featured products"]:
            heading_data = {
                "Product Section": heading,
                "Services": services
            }
            data.append(heading_data)
    return data

scraped_data = google_product_scraper()

#if scraped data array is not empty then write to json file, else break
if not scraped_data:
    print("No data to write to file")
    exit()
else:
    print("Data written to file")
    json_file_path = "GCP_Products.json"
    with open(json_file_path, "w") as json_file:
        json.dump(scraped_data, json_file, indent=4)
