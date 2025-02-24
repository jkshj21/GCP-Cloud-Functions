import re
import logging
from typing import Dict, Any, List, Union, Optional
from google.cloud.discoveryengine import (
    SearchServiceClient,
    DocumentServiceClient,
    SearchRequest,
    UserInfo,
    Interval,
    Document,
    ListDocumentsRequest,
    AnswerQueryRequest,
    ConversationalSearchServiceClient,
    ConverseConversationRequest
    )
from google.cloud.discoveryengine_v1beta import types
from dfcx_scrapi.core import scrapi_base

class Search(scrapi_base.ScrapiBase):
    """
    A class to interact with Google Cloud Discovery Engine Search APIs.
    """

    def __init__(
        self,
        creds_path: str = None,
        creds_dict: Dict = None,
        creds=None,
        scope=False,
    ):
        """
        Initializes the Search class with credentials.

        Args:
            creds_path (str, optional): Path to the credentials JSON file. Defaults to None.
            creds_dict (Dict, optional): Dictionary containing credentials. Defaults to None.
            creds (Any, optional): Credentials object. Defaults to None.
            scope (bool, optional): Whether to use scope. Defaults to False.
        """
        super().__init__(
            creds_path=creds_path,
            creds_dict=creds_dict,
            creds=creds,
            scope=scope,
        )

    @staticmethod
    def build_image_query(
        search_request: Dict[str, Any]
    ) -> Union[SearchRequest.ImageQuery, None]:
        """
        Builds an ImageQuery object from a search request dictionary.

        Args:
            search_request (Dict[str, Any]): Dictionary containing search request parameters.

        Returns:
            Union[SearchRequest.ImageQuery, None]: ImageQuery object or None if not found.
        """
        image_query = search_request.get("image_query", None)
        if image_query:
            image_bytes = image_query.get("image_bytes", None)
            return SearchRequest.ImageQuery(image_bytes=image_bytes)

        else:
            return None
    @staticmethod
    def build_user_info(
        search_request: Dict[str, Any]
    ) -> Union[UserInfo, None]:
        """
        Builds a UserInfo object from a search request dictionary.

        Args:
            search_request (Dict[str, Any]): Dictionary containing search request parameters.

        Returns:
            Union[UserInfo, None]: UserInfo object or None if not found.
        """
        user_info = search_request.get("user_info", None)
        if user_info:
            user_id = user_info.get("user_id", None)
            user_agent = user_info.get("user_agent", None)
            return UserInfo(user_id=user_id, user_agent=user_agent)

        else:
            return None

    def build_facet_specs(
        self, search_request: Dict[str, Any]
    ) -> Union[List[SearchRequest.FacetSpec], None]:
        """
        Builds a list of FacetSpec objects from a search request dictionary.

        Args:
            search_request (Dict[str, Any]): Dictionary containing search request parameters.

        Returns:
            Union[List[SearchRequest.FacetSpec], None]: List of FacetSpec objects or None if not found.
        """
        facet_specs = search_request.get("facet_specs", None)
        if facet_specs:
            all_specs = []
            for spec in facet_specs:
                all_specs.append(self.build_single_facet_spec(spec))

            return all_specs

        else:
            return None

    def build_spell_correction_spec(
        self, search_request: Dict[str, Any]
    ) -> Union[SearchRequest.SpellCorrectionSpec, None]:
        """
        Builds a SpellCorrectionSpec object from a search request dictionary.

        Args:
            search_request (Dict[str, Any]): Dictionary containing search request parameters.

        Returns:
            Union[SearchRequest.SpellCorrectionSpec, None]: SpellCorrectionSpec object or None if not found.
        """
        spell_spec_dict = search_request.get("spell_correction_spec", None)
        if spell_spec_dict:
            mode = self.get_spell_correct_mode_from_map(spell_spec_dict)
            return SearchRequest.SpellCorrectionSpec(mode=mode)

        else:
            return None

    def build_spell_correction_spec(
        self, search_request: Dict[str, Any]
    ) -> Union[SearchRequest.SpellCorrectionSpec, None]:
        """
        Builds a ContentSearchSpec object from a search request dictionary.

        Args:
            search_request (Dict[str, Any]): Dictionary containing search request parameters.

        Returns:
            Union[SearchRequest.ContentSearchSpec, None]: ContentSearchSpec object or None if not found.
        """
        spell_spec_dict = search_request.get("spell_correction_spec", None)
        if spell_spec_dict:
            mode = self.get_spell_correct_mode_from_map(spell_spec_dict)
            return SearchRequest.SpellCorrectionSpec(mode=mode)

        else:
            return None

    def build_content_search_spec(
        self, search_request: Dict[str, Any]
    ) -> Union[SearchRequest.ContentSearchSpec, None]:
        """
        Builds an EmbeddingSpec object from a search request dictionary.

        Args:
            search_request (Dict[str, Any]): Dictionary containing search request parameters.

        Returns:
            Union[SearchRequest.EmbeddingSpec, None]: EmbeddingSpec object or None if not found.
        """
        content_spec_dict = search_request.get("content_search_spec", None)
        if content_spec_dict:
            snippet_spec = self.build_snippet_spec()
            summary_spec = self.build_summary_spec(content_spec_dict)
            extractive_content_spec = self.build_extractive_content_spec(
                content_spec_dict
            )

            return SearchRequest.ContentSearchSpec(
                snippet_spec=snippet_spec,
                summary_spect=summary_spec,
                extractive_content_spec=extractive_content_spec,
            )

        else:
            return None

    def build_embedding_spec(
        self, search_request: Dict[str, Any]
    ) -> Union[SearchRequest.EmbeddingSpec, None]:
        """
        Builds a EmbeddingSpec object from a search request dictionary.

        Args:
            search_request (Dict[str, Any]): Dictionary containing search request parameters.

        Returns:
            Union[SearchRequest.EmbeddingSpec, None]: EmbeddingSpec object or None if not found.
        """
        embedding_vectors_dict = search_request.get("embedding_vectors", None)
        if embedding_vectors_dict:
            vector_list = embedding_vectors_dict.get("embedding_vectors", None)
            all_vectors = []
            for vector_dict in vector_list:
                all_vectors.append(self.build_embedding_vector(vector_dict))
            return SearchRequest.EmbeddingSpec(
                embedding_vectors=all_vectors
            )

        else:
            return None

    def build_query_expansion_spec(
        self, search_request: Dict[str, Any]
    ) -> Union[SearchRequest.QueryExpansionSpec, None]:
        """
        Builds a QueryExpansionSpec object from a search request dictionary.

        Args:
            search_request (Dict[str, Any]): Dictionary containing search request parameters.

        Returns:
            Union[SearchRequest.QueryExpansionSpec, None]: QueryExpansionSpec object or None if not found.
        """
        exp_spec_dict = search_request.get("query_expansion_spec", None)
        if exp_spec_dict:
            condition = self.get_condition_from_map(exp_spec_dict)
            pin_unexpanded_results = exp_spec_dict.get(
                "pin_unexpanded_results", False
            )

            return SearchRequest.QueryExpansionSpec(
                condition=condition,
                pin_unexpanded_results=pin_unexpanded_results,
            )

        else:
            return None

    def build_boost_spec(
        self, search_request: Dict[str, Any]
    ) -> Union[SearchRequest.BoostSpec, None]:
        """
        Builds a BoostSpec object from a search request dictionary.

        Args:
            search_request (Dict[str, Any]): Dictionary containing search request parameters.

        Returns:
            Union[SearchRequest.BoostSpec, None]: BoostSpec object or None if not found.
        """
        boost_spec_dict = search_request.get("boost_spec", None)
        if boost_spec_dict:
            condition_boost_specs = boost_spec_dict.get(
                "condition_boost_specs", None
            )
            all_boost_specs = []
            for spec in condition_boost_specs:
                all_boost_specs.append(self.build_condition_boost_spec(spec))
            return SearchRequest.BoostSpec(
                condition_boost_specs=all_boost_specs
            )

        else:
            return None

	# pylint: disable=C0301
    def query_by_search(self, search_config: Dict[str, Any], total_results: int = 10):
        """Performs a search against an indexed Vertex Data Store.

        Args:
        	search_config: A dictionary containing keys that correspond to the
            	SearchRequest attributes as defined in:
                https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine.SearchRequest
                For complex attributes that require nested fields, you can pass
                in another Dictionary as the value.

				Example: To represent the complex facet_specs config with some
				other simple parameters, you would do the following.

				```py
				search_config = {
				"facet_specs": [
						{
						"facet_key": {
								"key": "my_key",
								"intervals": [
								{
										"minimum": .5
									},
									{
										"maximum": .95
									}
								],
								"case_insensitive": True
							},
							"limit": 10
						}
					],
					"page_size": 10,
					"offset": 2
				}
			total_results: Total number of results to return for the search. If
				not specified, will default to 10 results. Increasing this to a
				high number can result in long search times.

        Returns:
                A List of SearchResponse objects.
        """
        serving_config = (
            f"{search_config.get('data_store_id', None)}"
            "/servingConfigs/default_serving_config"
        )

        branch_stub = "/".join(serving_config.split("/")[0:8])
        branch = branch_stub + "/branches/0"

        request = SearchRequest(
            serving_config=serving_config,
            branch=branch,
            query=search_config.get("query", None),
            image_query=self.build_image_query(search_config),
            page_size=search_config.get("page_size", 10),
            page_token=search_config.get("page_token", None),
            offset=search_config.get("offset", 0),
            filter=search_config.get("filter", None),
            canonical_filter=search_config.get("canonical_filter", None),
            order_by=search_config.get("order_by", None),
            user_info=self.build_user_info(search_config),
            facet_specs=self.build_facet_specs(search_config),
            boost_spec=self.build_boost_spec(search_config),
            params=search_config.get("params", None),
            query_expansion_spec=self.build_query_expansion_spec(search_config),
            spell_correction_spec=self.build_spell_correction_spec(
                search_config
            ),
            user_pseudo_id=search_config.get("user_pseudo_id", None),
            content_search_spec=self.build_content_search_spec(search_config),
            embedding_spec=self.build_embedding_spec(search_config),
            ranking_expression=search_config.get("ranking_expression", None),
            safe_search=search_config.get("safe_search", False),
            user_labels=search_config.get("user_labels", None),
        )

        client_options = self._client_options_discovery_engine(serving_config)
        client = SearchServiceClient(
            credentials=self.creds, client_options=client_options
        )
        response = client.search(request)

        all_results = []
        for search_result in response:
            if len(all_results) < total_results:
                all_results.append(search_result)
            else:
                break

        return all_results

    def query_by_answer(
        self,
        answer_config: Dict[str, Any],
        total_results: int = 10,
        related_question: bool = False):
        """
        Queries for an answer and related questions using Discovery Engine's AnswerQuery API.

        Args:
            answer_config (Dict[str, Any]): A dictionary containing configuration parameters for the AnswerQueryRequest.
                Must include 'data_store_id' and 'query'. Can also include 'user_labels' and 'session'.
            total_results (int, optional): The total number of results to return. Defaults to 10.
            related_question (bool, optional): Whether to enable related questions in the response. Defaults to False.

        Returns:
            google.cloud.discoveryengine_v1beta.types.AnswerQueryResponse: The response from the AnswerQuery API.
        """
        serving_config = (
            f"{answer_config.get('data_store_id', None)}"
            "/servingConfigs/default_serving_config"
        )
        query = types.Query(
            text=answer_config.get("query")
        )
        request = AnswerQueryRequest(
            serving_config=serving_config,
            query=query,
            user_labels=answer_config.get("user_labels", None),
            session=answer_config.get("session", None)
        )
        request.related_questions_spec.enable = related_question
        client_options = self._client_options_discovery_engine(serving_config)
        client = ConversationalSearchServiceClient(
            credentials=self.creds, client_options=client_options
        )
        response = client.answer_query(request)
        return response

    def query_by_conversation(
        self,
        conv_config: Dict[str, Any],
        conversation: types.conversation = None,
        ):
        """
        Queries for a conversation using Discovery Engine's ConverseConversation API.

        Args:
            conv_config (Dict[str, Any]): A dictionary containing configuration parameters for the ConverseConversationRequest.
                Must include 'data_store_id' and 'query'.
            conversation (google.cloud.discoveryengine_v1beta.types.conversation, optional): An existing Conversation object.
                If provided, the query is added to this conversation. Otherwise, a new conversation is started. Defaults to None.

        Returns:
            google.cloud.discoveryengine_v1beta.types.ConverseConversationResponse: The response from the ConverseConversation API.
        """
        serving_config = (
            f"{conv_config.get('data_store_id', None)}"
            "/servingConfigs/default_serving_config"
        )
        converse_name = f"{conv_config.get('data_store_id')}/conversations/-" if not conversation else conversation.name
        query = types.TextInput(
            input=conv_config.get("query")
        )
        
        request = ConverseConversationRequest(
            name=converse_name,
            query=query,
            serving_config=serving_config,
            conversation=conversation
        )

        client_options = self._client_options_discovery_engine(serving_config)
        client = ConversationalSearchServiceClient(
            credentials=self.creds, client_options=client_options
        )
        response = client.converse_conversation(request)

        return response
