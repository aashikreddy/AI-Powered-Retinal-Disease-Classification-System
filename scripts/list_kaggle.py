from kagglesdk.datasets.services.dataset_api_client import DatasetApiClient
from kagglehub.clients import KaggleApiV1Client
try:
    client = KaggleApiV1Client()
    response = client.get(f"/datasets/v1/mariaherrerot/aptos2019")
    print(response)
except Exception as e:
    print(e)
