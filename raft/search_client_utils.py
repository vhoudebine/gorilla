from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import random

class AzureSearchClient:
    def __init__(self, endpoint, index_name, api_key):
        """
        Initializes the AzureSearchClient with the given endpoint, index name, and API key.

        :param endpoint: The endpoint of the Azure Search service.
        :param index_name: The name of the index to search.
        :param api_key: The API key for the Azure Search service.
        """
        self.endpoint = endpoint
        self.index_name = index_name
        self.api_key = api_key
        self.client = SearchClient(endpoint=self.endpoint,
                                   index_name=self.index_name,
                                   credential=AzureKeyCredential(self.api_key))

    def get_all_documents(self):
        """
        Retrieves all documents from the Azure Search index using pagination.

        :return: A list of all documents in the index.
        """
        all_documents = []
        page_size = 1000   # Maximum page size
        skip = 0
        total_count = None

        # Initial search to get total count
        results = self.client.search(
            search_text="*",
            top=0,
            include_total_count=True
        )
        total_count = results.get_count()
        if total_count is None:
            raise Exception("Unable to retrieve the total count of documents.")
        print(f"Total documents found: {total_count}")

        while skip < total_count:
            results = self.client.search(
                search_text="*",
                top=page_size,
                skip=skip
            )
            documents = list(results)
            all_documents.extend(documents)
            skip += page_size
            print(f"Fetched {len(all_documents)} of {total_count} documents.")

        return all_documents

    def get_random_sample(self, n):
        """
        Returns a random sample of n documents from the index.

        :param n: The number of documents to sample.
        :return: A list of n randomly sampled documents.
        """
        all_documents = self.get_all_documents()
        if n > len(all_documents):
            raise ValueError(f"Requested sample size {n} exceeds the total number of documents {len(all_documents)}.")
        return random.sample(all_documents, n)