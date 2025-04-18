from typing import final

from azure.search.documents import SearchClient
from azure.search.documents.models import QueryAnswerType, QueryCaptionType, QueryType, VectorizedQuery
from openai.lib.azure import AzureOpenAI

from definitions import SearchIndexResults
from util import AzureOpenAIEmbeddings, AzureOpenAIModels


@final
class AzureSearchIndex:
    """
    Utility class for searching the index.
    """

    @staticmethod
    def _get_vectorized_query(openai_client: AzureOpenAI, query: str) -> VectorizedQuery:
        """
        Generates embeddings for the query and returns it as a vectorized query.
        :param openai_client: The Azure OpenAI client.
        :param query: The search query.
        :return: A vectorized query.
        """
        embeddings = AzureOpenAIEmbeddings.generate(openai_client, model=AzureOpenAIModels.TEXT_EMBEDDING_ADA_002,
                                                    text=query)

        return VectorizedQuery(fields="embeddings", k_nearest_neighbors=3, vector=embeddings[0])

    @staticmethod
    def do_hybrid_search(openai_client: AzureOpenAI, search_client: SearchClient, *, query: str,
                         top_results: int = 5) -> SearchIndexResults:
        """
        Performs a hybrid search on the index.
        :param openai_client: The Azure OpenAI client.
        :param search_client: The search client.
        :param query: The search query.
        :param top_results: The number of top results to return. The default value is 5.
        :return: The search results.
        """
        vector_query = AzureSearchIndex._get_vectorized_query(openai_client, query)

        # Do search.
        results = search_client.search(search_text=query, select=("Name", "Description", "Code"), top=top_results,
                                       vector_queries=[vector_query])

        # Return the search results.
        return [(result["Name"], result["Description"], result["Code"]) for result in results]

    @staticmethod
    def do_semantic_reranker_search(openai_client: AzureOpenAI, search_client: SearchClient, *,
                                    semantic_configuration_name: str, query: str,
                                    top_results: int = 5) -> SearchIndexResults:
        """
        Performs a semantic reranking search on the index.
        :param openai_client: The Azure OpenAI client.
        :param search_client: The search client.
        :param semantic_configuration_name: The semantic configuration name.
        :param query: The search query.
        :param top_results: The number of top results to return. The default value is 5.
        :return: The search results.
        """
        vector_query = AzureSearchIndex._get_vectorized_query(openai_client, query)

        # Do search.
        results = search_client.search(query_answer=QueryAnswerType.EXTRACTIVE,
                                       query_caption=QueryCaptionType.EXTRACTIVE, query_type=QueryType.SEMANTIC,
                                       search_text=query, select=("Name", "Description", "Code"),
                                       semantic_configuration_name=semantic_configuration_name, top=top_results,
                                       vector_queries=[vector_query])

        # Return the search results.
        return [(result["Name"], result["Description"], result["Code"]) for result in results]
