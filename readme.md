# Google Cloud Platform Product List

![Daily Scraping Status](https://github.com/REllwood/gcp-product-list/actions/workflows/daily-scraping.yml/badge.svg)


This repository fetches all current GCP products and services from the [GCP Products and Services page](https://cloud.google.com/products/) and stores them in a JSON file daily. A Github Action is used to run the script daily and refresh the data daily.

# Data Format   

All data is stored in the GCP_Products.json file. The format is as follows:
```json
     "Product Section": "AI and Machine Learning",
        "Services": [
            {
                "ProductName": "Vertex AI",
                "Description": "Unified platform for training, hosting, and managing ML models."
            },
            {
                "ProductName": "Vertex AI Workbench",
                "Description": "A single interface for your data, analytics, and machine learning workflow."
            },
            {
                "ProductName": "Vertex Explainable AI",
                "Description": "Tools and frameworks to understand and interpret your machine learning models."
            }
```

I feel this format is the most useful for developers who want to use this data in their own projects.

<Strong>Keys:</Strong>
- **Product Section:** The section of the GCP Products and Services page the product is listed under.
- **ProductName:** The name of the GCP product.
- **Description:** A short description of the product.
