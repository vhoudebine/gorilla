from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import random
import os
import json
import tempfile

def _get_env_var():
    """
    Helper function to get an environment variable or return a default value.

    :param var_name: The name of the environment variable.
    :param default: The default value to return if the environment variable is not set.
    :return: The value of the environment variable or the default value.
    """
    return os.getenv("AZURE_AI_SEARCH_ENDPOINT"), os.getenv("AZURE_AI_SEARCH_KEY") 

class AzureSearchClient:
    def __init__(self, index_name):
        """
        Initializes the AzureSearchClient with the given endpoint, index name, and API key.

        :param endpoint: The endpoint of the Azure Search service.
        :param index_name: The name of the index to search.
        :param api_key: The API key for the Azure Search service.
        """
        endpoint, api_key = _get_env_var()
        self.endpoint = endpoint
        self.index_name = index_name
        self.api_key = api_key
        self.client = SearchClient(endpoint=self.endpoint,
                                   index_name=self.index_name,
                                   credential=AzureKeyCredential(self.api_key))

    def get_all_documents(self):
        """
        Retrieves all documents from the Azure Search index using pagination and writes each page to a temp JSONL file.

        :return: The path to the temp JSONL file containing all documents.
        """
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

        temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.jsonl')
        temp_file_path = temp_file.name

        while skip < total_count:
            results = self.client.search(
            search_text="*",
            top=page_size,
            skip=skip
            )
            documents = list(results)
            for doc in documents:
                temp_file.write(json.dumps(doc) + '\n')
            skip += len(documents)
            print(f"Fetched {skip} of {total_count} documents.")

        temp_file.close()
        return temp_file_path

    def get_random_sample(self, n):
        """
        Returns a random sample of n documents from the index by reading from the temp JSONL file.

        :param n: The number of documents to sample.
        :return: A list of n randomly sampled documents.
        """
        temp_file_path = self.get_all_documents()
        sample = []
        with open(temp_file_path, 'r') as temp_file:
            lines = temp_file.readlines()
            total_count = len(lines)
            if total_count < n:
                raise ValueError(f"Requested sample size {n} exceeds the total number of documents {total_count}.")
            sample_indices = random.sample(range(total_count), n)
            sample = [json.loads(lines[i]) for i in sample_indices]

        return sample
