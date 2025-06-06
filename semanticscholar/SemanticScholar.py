from typing import List, Literal, Tuple, Union
import asyncio
import nest_asyncio

from semanticscholar.PaginatedResults import PaginatedResults
from semanticscholar.AsyncSemanticScholar import AsyncSemanticScholar
from semanticscholar.Author import Author
from semanticscholar.Paper import Paper
from semanticscholar.Autocomplete import Autocomplete
from semanticscholar.Citation import Citation
from semanticscholar.Reference import Reference


class SemanticScholar():
    '''
    Main class to retrieve data from Semantic Scholar Graph API synchronously.
    '''

    def __init__(
                self,
                timeout: int = 30,
                api_key: str = None,
                api_url: str = None,
                debug: bool = False,
                retry: bool = True,
                requests_per_second: float = None, # Added requests_per_second
            ) -> None:
        '''
        :param float timeout: (optional) an exception is raised
               if the server has not issued a response for timeout seconds.
        :param str api_key: (optional) private API key.
        :param str api_url: (optional) custom API url.
        :param bool debug: (optional) enable debug mode.
        :param bool retry: enable retry mode.
        :param float requests_per_second: (optional) maximum number of requests to make per second to the API.
        '''
        nest_asyncio.apply()
        self._timeout = timeout
        self._retry = retry
        self._AsyncSemanticScholar = AsyncSemanticScholar(
            timeout=timeout,
            api_key=api_key,
            api_url=api_url,
            debug=debug,
            retry=retry,
            requests_per_second=requests_per_second # Pass to AsyncSemanticScholar
        )
        self.debug = debug

    @property
    def timeout(self) -> int:
        '''
        Timeout for server response in seconds.

        :type: :class:`int`
        '''
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: int) -> None:
        '''
        :param int timeout:
        '''
        self._timeout = timeout
        self._AsyncSemanticScholar.timeout = timeout
    
    @property
    def debug(self) -> bool:
        '''
        Enable/disable debug mode.

        :type: :class:`bool`

        .. deprecated:: 0.8.4
            Use Python\'s standard logging in DEBUG level instead.
        '''
        return self._debug
    
    @debug.setter
    def debug(self, debug: bool) -> None:
        '''
        :param bool debug:
        '''
        self._debug = debug
        self._AsyncSemanticScholar.debug = debug

    @property
    def retry(self) -> bool:
        '''
        Enable/disable retry mode.

        :type: :class:`bool`
        '''
        return self._retry
    
    @retry.setter
    def retry(self, retry: bool) -> None:
        '''
        :param bool retry:
        '''
        self._retry = retry
        self._AsyncSemanticScholar.retry = retry

    def get_paper(
                self,
                paper_id: str,
                fields: list = None
            ) -> Paper:
        '''
        Paper lookup

        :calls: `GET /graph/v1/paper/{paper_id} \
            <https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data\
            /operation/get_graph_get_paper>`_

        :param str paper_id: S2PaperId, CorpusId, DOI, ArXivId, MAG, ACL, 
               PMID, PMCID, or URL from:

               - semanticscholar.org
               - arxiv.org
               - aclweb.org
               - acm.org
               - biorxiv.org

        :param list fields: (optional) list of the fields to be returned.
        :returns: paper data
        :rtype: :class:`semanticscholar.Paper.Paper`
        :raises: ObjectNotFoundException: if Paper ID not found.
        '''

        loop = asyncio.get_event_loop()
        paper = loop.run_until_complete(
            self._AsyncSemanticScholar.get_paper(
                paper_id=paper_id, 
                fields=fields
                )
        )

        return paper

    def get_papers(
                self,
                paper_ids: List[str],
                fields: list = None,
                return_not_found: bool = False
            ) -> Union[List[Paper], Tuple[List[Paper], List[str]]]:
        '''
        Get details for multiple papers at once

        :calls: `POST /graph/v1/paper/batch \
            <https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data\
            /operation/post_graph_get_papers>`_

        :param str paper_ids: list of IDs (must be <= 500) - S2PaperId, 
            CorpusId, DOI, ArXivId, MAG, ACL, PMID, PMCID, or URL from:

            - semanticscholar.org
            - arxiv.org
            - aclweb.org
            - acm.org
            - biorxiv.org

        :param list fields: (optional) list of the fields to be returned.
        :param bool return_not_found: (optional) flag to include not found IDs 
               in the return, except for IDs in URL:<url> format.
        :returns: papers data, and optionally list of IDs not found.
        :rtype: :class:`List` of :class:`semanticscholar.Paper.Paper` 
                or :class:`Tuple` [:class:`List` of 
                :class:`semanticscholar.Paper.Paper`, 
                :class:`List` of :class:`str`]
        :raises: BadQueryParametersException: if no paper was found.
        '''

        loop = asyncio.get_event_loop()
        papers = loop.run_until_complete(
            self._AsyncSemanticScholar.get_papers(
                paper_ids=paper_ids,
                fields=fields,
                return_not_found=return_not_found
                )
        )

        return papers

    def get_paper_authors(
                self,
                paper_id: str,
                fields: list = None,
                limit: int = 100
            ) -> PaginatedResults:
        '''
        Get details about a paper's authors

        :calls: `POST /graph/v1/paper/{paper_id}/authors \
            <https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data\
            /operation/get_graph_get_paper_authors>`_

        :param str paper_id: S2PaperId, CorpusId, DOI, ArXivId, MAG, ACL, 
               PMID, PMCID, or URL from:

               - semanticscholar.org
               - arxiv.org
               - aclweb.org
               - acm.org
               - biorxiv.org

        :param list fields: (optional) list of the fields to be returned.
        :param int limit: (optional) maximum number of results to return 
               (must be <= 1000).
        '''

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self._AsyncSemanticScholar.get_paper_authors(
                paper_id=paper_id,
                fields=fields,
                limit=limit
                )
        )

        return results

    def get_paper_authors_complete(
            self,
            paper_id: str,
            fields: list = None,
            limit: int = 100,
            max_authors: int = None
        ) -> List[Author]:
        '''
        Get complete list of a paper's authors without pagination.
        This method handles pagination internally and returns all authors
        up to an optional maximum.

        :param str paper_id: S2PaperId, CorpusId, DOI, ArXivId, MAG, ACL, 
               PMID, PMCID, or URL from:
               - semanticscholar.org
               - arxiv.org
               - aclweb.org
               - acm.org
               - biorxiv.org
        :param list fields: (optional) list of the fields to be returned for each author.
        :param int limit: (optional) number of results to return per underlying API
               call (page size). Must be <= 1000. Default is 100.
        :param int max_authors: (optional) maximum total number of authors to return.
               If None, all authors are returned.
        :returns: List of :class:`semanticscholar.Author.Author` objects.
        :rtype: :class:`List` of :class:`semanticscholar.Author.Author`
        '''
        all_authors = []
        # The 'limit' passed to get_paper_authors here acts as the page size
        # for the PaginatedResults object.
        paginated_results = self.get_paper_authors(
            paper_id=paper_id,
            fields=fields,
            limit=limit
        )

        for author_item in paginated_results:  # Iterating PaginatedResults handles fetching all pages
            if max_authors is not None and len(all_authors) >= max_authors:
                break  # Stop collecting once we've reached max_authors
            all_authors.append(author_item)

        return all_authors

    def get_paper_citations(
            self,
            paper_id: str,
            fields: list = None,
            limit: int = 100
        ) -> PaginatedResults:
        '''
        Get details about a paper's citations

        :calls: `POST /graph/v1/paper/{paper_id}/citations \
            <https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data\
            /operation/get_graph_get_paper_citations>`_

        :param str paper_id: S2PaperId, CorpusId, DOI, ArXivId, MAG, ACL, 
               PMID, PMCID, or URL from:

               - semanticscholar.org
               - arxiv.org
               - aclweb.org
               - acm.org
               - biorxiv.org

        :param list fields: (optional) list of the fields to be returned.
        :param int limit: (optional) maximum number of results to return 
               (must be <= 1000).
        '''

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self._AsyncSemanticScholar.get_paper_citations(
                paper_id=paper_id,
                fields=fields,
                limit=limit
                )
        )

        return results

    def get_paper_citations_complete(
            self,
            paper_id: str,
            fields: list = None,
            limit: int = 100,
            max_citations: int = None
        ) -> List[Citation]:
        '''
        Get complete list of a paper's citations without pagination.
        This method handles pagination internally and returns all citations
        up to an optional maximum.

        :param str paper_id: S2PaperId, CorpusId, DOI, ArXivId, MAG, ACL, 
               PMID, PMCID, or URL from:
               - semanticscholar.org
               - arxiv.org
               - aclweb.org
               - acm.org
               - biorxiv.org
        :param list fields: (optional) list of the fields to be returned for each citation.
        :param int limit: (optional) number of results to return per underlying API
               call (page size). Must be <= 1000. Default is 100.
        :param int max_citations: (optional) maximum total number of citations to return.
               If None, all citations are returned.
        :returns: List of :class:`semanticscholar.Citation.Citation` objects.
        :rtype: :class:`List` of :class:`semanticscholar.Citation.Citation`
        '''
        all_citations = []
        paginated_results = self.get_paper_citations(
            paper_id=paper_id,
            fields=fields,
            limit=limit
        )

        for citation_item in paginated_results:
            if max_citations is not None and len(all_citations) >= max_citations:
                break
            all_citations.append(citation_item)

        return all_citations

    def get_paper_references(
            self,
            paper_id: str,
            fields: list = None,
            limit: int = 100
        ) -> PaginatedResults:
        '''
        Get details about a paper's references

        :calls: `POST /graph/v1/paper/{paper_id}/references \
            <https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data\
            /operation/get_graph_get_paper_references>`_

        :param str paper_id: S2PaperId, CorpusId, DOI, ArXivId, MAG, ACL, 
               PMID, PMCID, or URL from:

               - semanticscholar.org
               - arxiv.org
               - aclweb.org
               - acm.org
               - biorxiv.org

        :param list fields: (optional) list of the fields to be returned.
        :param int limit: (optional) maximum number of results to return 
               (must be <= 1000).
        '''

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self._AsyncSemanticScholar.get_paper_references(
                paper_id=paper_id,
                fields=fields,
                limit=limit
                )
        )

        return results

    def get_paper_references_complete(
            self,
            paper_id: str,
            fields: list = None,
            limit: int = 100,
            max_references: int = None
        ) -> List[Reference]:
        '''
        Get complete list of a paper's references without pagination.
        This method handles pagination internally and returns all references
        up to an optional maximum.

        :param str paper_id: S2PaperId, CorpusId, DOI, ArXivId, MAG, ACL, 
               PMID, PMCID, or URL from:
               - semanticscholar.org
               - arxiv.org
               - aclweb.org
               - acm.org
               - biorxiv.org
        :param list fields: (optional) list of the fields to be returned for each reference.
        :param int limit: (optional) number of results to return per underlying API
               call (page size). Must be <= 1000. Default is 100.
        :param int max_references: (optional) maximum total number of references to return.
               If None, all references are returned.
        :returns: List of :class:`semanticscholar.Reference.Reference` objects.
        :rtype: :class:`List` of :class:`semanticscholar.Reference.Reference`
        '''
        all_references = []
        paginated_results = self.get_paper_references(
            paper_id=paper_id,
            fields=fields,
            limit=limit
        )

        for reference_item in paginated_results:
            if max_references is not None and len(all_references) >= max_references:
                break
            all_references.append(reference_item)

        return all_references

    def search_paper(
                self,
                query: str,
                year: str = None,
                publication_types: list = None,
                open_access_pdf: bool = None,
                venue: list = None,
                fields_of_study: list = None,
                fields: list = None,
                publication_date_or_year: str = None,
                min_citation_count: int = None,
                limit: int = 100,
                bulk: bool = False,
                sort: str = None,
                match_title: bool = False
            ) -> Union[PaginatedResults, Paper]:
        '''
        Search for papers by keyword. Performs a search query based on the 
        S2 search relevance algorithm, or a bulk retrieval of basic paper 
        data without search relevance (if bulk=True). Paper relevance 
        search is the default behavior and returns up to 1,000 results. 
        Bulk retrieval instead returns up to 10,000,000 results (1,000 
        in each page).

        :calls: `GET /graph/v1/paper/search \
                <https://api.semanticscholar.org/api-docs/graph#tag/\
                Paper-Data/operation/get_graph_paper_relevance_search>`_
        :calls: `GET /graph/v1/paper/search/bulk \
                <https://api.semanticscholar.org/api-docs/graph#tag/\
                Paper-Data/operation/get_graph_paper_bulk_search>`_

        :param str query: plain-text search query string.
        :param str year: (optional) restrict results to the given range of 
               publication year.
        :param list publication_type: (optional) restrict results to the given 
               publication type list.
        :param bool open_access_pdf: (optional) restrict results to papers 
               with public PDFs.
        :param list venue: (optional) restrict results to the given venue list.
        :param list fields_of_study: (optional) restrict results to given 
               field-of-study list, using the s2FieldsOfStudy paper field.
        :param list fields: (optional) list of the fields to be returned.
        :param str publication_date_or_year: (optional) restrict results to 
               the given range of publication date in the format 
               <start_date>:<end_date>, where dates are in the format 
               YYYY-MM-DD, YYYY-MM, or YYYY.
        :param int min_citation_count: (optional) restrict results to papers 
               with at least the given number of citations.
        :param int limit: (optional) maximum number of results to return 
               (must be <= 100).
        :param bool bulk: (optional) bulk retrieval of basic paper data 
               without search relevance (ignores the limit parameter if True 
               and returns up to 1,000 results in each page).
        :param str sort: (optional) sorts results (only if bulk=True) using 
               <field>:<order> format, where "field" is either paperId, 
               publicationDate, or citationCount, and "order" is asc 
               (ascending) or desc (descending).
        :param bool match_title: (optional) retrieve a single paper whose 
               title best matches the given query.
        :returns: query results.
        :rtype: :class:`semanticscholar.PaginatedResults.PaginatedResults` or 
            :class:`semanticscholar.Paper.Paper`
        '''

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self._AsyncSemanticScholar.search_paper(
                query=query,
                year=year,
                publication_types=publication_types,
                open_access_pdf=open_access_pdf,
                venue=venue,
                fields_of_study=fields_of_study,
                fields=fields,
                publication_date_or_year=publication_date_or_year,
                min_citation_count=min_citation_count,
                limit=limit,
                bulk=bulk,
                sort=sort,
                match_title=match_title
                )
        )

        return results
        
    def search_paper_complete(
            self,
            query: str,
            year: str = None,
            publication_types: list = None,
            open_access_pdf: bool = None,
            venue: list = None,
            fields_of_study: list = None,
            fields: list = None,
            publication_date_or_year: str = None,
            min_citation_count: int = None,
            limit: int = 100,
            bulk: bool = False,
            sort: str = None,
            max_papers: int = None
        ) -> List[Paper]:
        '''
        Search for papers by keyword and get complete list of results without pagination.
        This method handles pagination internally and returns all matching papers
        up to an optional maximum. Paper relevance search is the default behavior.
        Bulk retrieval instead returns up to 10,000,000 results (1,000 in each page).

        :param str query: plain-text search query string.
        :param str year: (optional) restrict results to the given range of 
               publication year.
        :param list publication_type: (optional) restrict results to the given 
               publication type list.
        :param bool open_access_pdf: (optional) restrict results to papers 
               with public PDFs.
        :param list venue: (optional) restrict results to the given venue list.
        :param list fields_of_study: (optional) restrict results to given 
               field-of-study list, using the s2FieldsOfStudy paper field.
        :param list fields: (optional) list of the fields to be returned.
        :param str publication_date_or_year: (optional) restrict results to 
               the given range of publication date in the format 
               <start_date>:<end_date>, where dates are in the format 
               YYYY-MM-DD, YYYY-MM, or YYYY.
        :param int min_citation_count: (optional) restrict results to papers 
               with at least the given number of citations.
        :param int limit: (optional) number of results to return per underlying API
               call (page size). Must be <= 100 for regular search or <= 1000 for bulk.
        :param bool bulk: (optional) bulk retrieval of basic paper data 
               without search relevance.
        :param str sort: (optional) sorts results (only if bulk=True) using 
               <field>:<order> format, where "field" is either paperId, 
               publicationDate, or citationCount, and "order" is asc 
               (ascending) or desc (descending).
        :param int max_papers: (optional) maximum total number of papers to return.
               If None, all matching papers are returned.
        :returns: List of :class:`semanticscholar.Paper.Paper` objects.
        :rtype: :class:`List` of :class:`semanticscholar.Paper.Paper`
        '''
        all_papers = []
        paginated_results = self.search_paper(
            query=query,
            year=year,
            publication_types=publication_types,
            open_access_pdf=open_access_pdf,
            venue=venue,
            fields_of_study=fields_of_study,
            fields=fields,
            publication_date_or_year=publication_date_or_year,
            min_citation_count=min_citation_count,
            limit=limit,
            bulk=bulk,
            sort=sort,
            match_title=False
        )

        for paper_item in paginated_results:
            if max_papers is not None and len(all_papers) >= max_papers:
                break
            all_papers.append(paper_item)

        return all_papers

    def get_author(
                self,
                author_id: str,
                fields: list = None
            ) -> Author:
        '''
        Author lookup

        :calls: `GET /graph/v1/author/{author_id} \
            <https://api.semanticscholar.org/api-docs/graph#tag/Author-Data\
            /operation/get_graph_get_author>`_

        :param str author_id: S2AuthorId.
        :returns: author data
        :rtype: :class:`semanticscholar.Author.Author`
        :raises: ObjectNotFoundException: if Author ID not found.
        '''

        loop = asyncio.get_event_loop()
        author = loop.run_until_complete(
            self._AsyncSemanticScholar.get_author(
                author_id=author_id,
                fields=fields
                )
        )

        return author

    def get_authors(
                self,
                author_ids: List[str],
                fields: list = None,
                return_not_found: bool = False
            ) -> Union[List[Author], Tuple[List[Author], List[str]]]:
        '''
        Get details for multiple authors at once

        :calls: `POST /graph/v1/author/batch \
            <https://api.semanticscholar.org/api-docs/graph#tag/Author-Data\
            /operation/get_graph_get_author>`_

        :param str author_ids: list of S2AuthorId (must be <= 1000).
        :returns: author data, and optionally list of IDs not found.
        :rtype: :class:`List` of :class:`semanticscholar.Author.Author` 
                or :class:`Tuple` [:class:`List` of 
                :class:`semanticscholar.Author.Author`, 
                :class:`List` of :class:`str`]
        :raises: BadQueryParametersException: if no author was found.
        '''

        loop = asyncio.get_event_loop()
        authors = loop.run_until_complete(
            self._AsyncSemanticScholar.get_authors(
                author_ids=author_ids,
                fields=fields,
                return_not_found=return_not_found
                )
        )

        return authors

    def get_author_papers(
                self,
                author_id: str,
                fields: list = None,
                limit: int = 100
            ) -> PaginatedResults:
        '''
        Get details about an author's papers.

        Returns a PaginatedResults object that allows iteration over all of an
        author's papers. The 'limit' parameter controls how many results are
        fetched per underlying API call (page size).

        :calls: `GET /graph/v1/author/{author_id}/papers \
            <https://api.semanticscholar.org/api-docs/graph#tag/Author-Data\
            /operation/get_graph_get_author_papers>`_

        :param str author_id: S2AuthorId.
        :param list fields: (optional) list of the fields to be returned.
        :param int limit: (optional) number of results to return per page 
               (must be <= 1000). Default is 100.
        '''

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self._AsyncSemanticScholar.get_author_papers(
                author_id=author_id,
                fields=fields,
                limit=limit
                )
        )

        return results

    def get_author_papers_complete(
                self,
                author_id: str,
                fields: list = None,
                limit: int = 100,
                max_papers: int = None
            ) -> List[Paper]:
        '''
        Get complete list of an author's papers without pagination.
        This method handles pagination internally and returns all papers
        up to an optional maximum.

        :param str author_id: S2AuthorId.
        :param list fields: (optional) list of the fields to be returned for each paper.
        :param int limit: (optional) number of results to return per underlying API
               call (page size). Must be <= 1000. Default is 100.
        :param int max_papers: (optional) maximum total number of papers to return.
               If None, all papers are returned.
        :returns: List of :class:`semanticscholar.Paper.Paper` objects.
        :rtype: :class:`List` of :class:`semanticscholar.Paper.Paper`
        '''
        all_papers = []
        # The 'limit' passed to get_author_papers here acts as the page size
        # for the PaginatedResults object.
        paginated_results = self.get_author_papers(
            author_id=author_id,
            fields=fields,
            limit=limit
        )

        for paper_item in paginated_results: # Iterating PaginatedResults handles fetching all pages
            if max_papers is not None and len(all_papers) >= max_papers:
                break  # Stop collecting once we've reached max_papers
            all_papers.append(paper_item)

        return all_papers

    def search_author(
                self,
                query: str,
                fields: list = None,
                limit: int = 100
            ) -> PaginatedResults:
        '''
        Search for authors by name

        :calls: `GET /graph/v1/author/search \
            <https://api.semanticscholar.org/api-docs/graph#tag/Author-Data\
            /operation/get_graph_get_author_search>`_

        :param str query: plain-text search query string.
        :param list fields: (optional) list of the fields to be returned.
        :param int limit: (optional) maximum number of results to return 
               (must be <= 1000).
        :returns: query results.
        :rtype: :class:`semanticscholar.PaginatedResults.PaginatedResults`
        '''

        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self._AsyncSemanticScholar.search_author(
                query=query,
                fields=fields,
                limit=limit
                )
        )

        return results
        
    def search_author_complete(
            self,
            query: str,
            fields: list = None,
            limit: int = 100,
            max_authors: int = None
        ) -> List[Author]:
        '''
        Get complete list of authors matching a search query without pagination.
        This method handles pagination internally and returns all matching authors
        up to an optional maximum.

        :param str query: plain-text search query string.
        :param list fields: (optional) list of the fields to be returned.
        :param int limit: (optional) number of results to return per underlying API
               call (page size). Must be <= 1000. Default is 100.
        :param int max_authors: (optional) maximum total number of authors to return.
               If None, all matching authors are returned.
        :returns: List of :class:`semanticscholar.Author.Author` objects.
        :rtype: :class:`List` of :class:`semanticscholar.Author.Author`
        '''
        all_authors = []
        paginated_results = self.search_author(
            query=query,
            fields=fields,
            limit=limit
        )

        for author_item in paginated_results:
            if max_authors is not None and len(all_authors) >= max_authors:
                break
            all_authors.append(author_item)

        return all_authors

    def get_recommended_papers(
                self,
                paper_id: str,
                fields: list = None,
                limit: int = 100,
                pool_from: Literal["recent", "all-cs"] = "recent"
            ) -> List[Paper]:
        '''
        Get recommended papers for a single positive example.

        :calls: `GET /recommendations/v1/papers/forpaper/{paper_id} \
            <https://api.semanticscholar.org/api-docs/recommendations#\
            tag/Paper-Recommendations/operation/get_papers_for_paper>`_

        :param str paper_id: S2PaperId, CorpusId, DOI, ArXivId, MAG, ACL, 
               PMID, PMCID, or URL from:

               - semanticscholar.org
               - arxiv.org
               - aclweb.org
               - acm.org
               - biorxiv.org

        :param list fields: (optional) list of the fields to be returned.
        :param int limit: (optional) maximum number of recommendations to 
               return (must be <= 500).
        :param str pool_from: (optional) which pool of papers to recommend 
               from. Must be either "recent" or "all-cs".
        :returns: list of recommendations.
        :rtype: :class:`List` of :class:`semanticscholar.Paper.Paper`
        '''

        loop = asyncio.get_event_loop()
        papers = loop.run_until_complete(
            self._AsyncSemanticScholar.get_recommended_papers(
                paper_id=paper_id,
                fields=fields,
                limit=limit,
                pool_from=pool_from
                )
        )

        return papers

    def get_recommended_papers_from_lists(
                self,
                positive_paper_ids: List[str],
                negative_paper_ids: List[str] = None,
                fields: list = None,
                limit: int = 100
            ) -> List[Paper]:
        '''
        Get recommended papers for lists of positive and negative examples.

        :calls: `POST /recommendations/v1/papers/ \
            <https://api.semanticscholar.org/api-docs/recommendations#\
            tag/Paper-Recommendations/operation/post_papers>`_

        :param list positive_paper_ids: list of paper IDs 
               that the returned papers should be related to.
        :param list negative_paper_ids: (optional) list of paper IDs 
               that the returned papers should not be related to.
        :param list fields: (optional) list of the fields to be returned.
        :param int limit: (optional) maximum number of recommendations to 
               return (must be <= 500).
        :returns: list of recommendations.
        :rtype: :class:`List` of :class:`semanticscholar.Paper.Paper`
        '''

        loop = asyncio.get_event_loop()
        papers = loop.run_until_complete(
            self._AsyncSemanticScholar.get_recommended_papers_from_lists(
                positive_paper_ids=positive_paper_ids,
                negative_paper_ids=negative_paper_ids,
                fields=fields,
                limit=limit
                )
        )

        return papers
    
    def get_autocomplete(self, query: str) -> List[Autocomplete]:
        """
        Get autocomplete suggestions for a paper query.

        :calls: `GET /graph/v1/paper/autocomplete?query={query} \
            <https://api.semanticscholar.org/api-docs/graph#tag/\
            Paper-Data/operation/get_graph_get_paper_autocomplete>`_

        :param str query: query to get autocomplete suggestions for.
        :returns: list of autocomplete suggestions.
        :rtype: :class:`List` of 
                :class:`semanticscholar.Autocomplete.Autocomplete`
        """
        
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(
            self._AsyncSemanticScholar.get_autocomplete(query=query)
        )

        return results
