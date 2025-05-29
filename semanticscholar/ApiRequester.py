import asyncio
import json
import logging
import time # Added for rate limit delay measurement
import warnings
from typing import List, Union

import httpx
from tenacity import retry as rerun
from tenacity import retry_if_exception_type, stop_after_attempt, wait_fixed

from aiolimiter import AsyncLimiter # Added for throttling

from semanticscholar.SemanticScholarException import (
    BadQueryParametersException, GatewayTimeoutException,
    InternalServerErrorException, ObjectNotFoundException)

logger = logging.getLogger('semanticscholar')


class ApiRequester:

    def __init__(self, timeout, retry: bool = True, requests_per_second: float = None) -> None: # Added requests_per_second
        '''
        :param float timeout: an exception is raised 
               if the server has not issued a response for timeout seconds.
        :param bool retry: enable retry mode.
        :param float requests_per_second: (optional) maximum number of requests to make per second to the API.
        '''
        self.timeout = timeout
        self.retry = retry

        self._limiter = None # Initialize limiter to None (off by default)
        if requests_per_second is not None and requests_per_second > 0:
            if requests_per_second >= 1.0:
                # X requests per 1 second
                rate = int(round(requests_per_second)) # aiolimiter expects int for rate
                period = 1.0
            else:
                # 1 request per Y seconds (where Y = 1/requests_per_second)
                rate = 1
                period = 1.0 / requests_per_second
            self._limiter = AsyncLimiter(rate, period)
            logger.info(f"ApiRequester throttling enabled: {rate} request(s) per {period:.2f} second(s).")

    @property
    def timeout(self) -> int:
        '''
        :type: :class:`int`
        '''
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: int) -> None:
        '''
        :param int timeout:
        '''
        self._timeout = timeout

    @property
    def retry(self) -> bool:
        '''
        :type: :class:`bool`
        '''
        return self._retry
    
    @retry.setter
    def retry(self, retry: bool) -> None:
        '''
        :param bool retry:
        '''
        self._retry = retry

    def _curl_cmd(
                self,
                url: str,
                method: str,
                headers: dict,
                payload: dict = None
            ) -> str:
        curl_cmd = f'curl -X {method}'
        if headers:
            for key, value in headers.items():
                curl_cmd += f' -H \'{key}: {value}\''
        curl_cmd += f' -d \'{json.dumps(payload)}\'' if payload else ''
        curl_cmd += f' {url}'
        return curl_cmd

    async def get_data_async(
        self,
        url: str,
        parameters: str,
        headers: dict,
        payload: dict = None
    ) -> Union[dict, List[dict]]:
        '''
        Get data from Semantic Scholar API

        :param str url: absolute URL to API endpoint.
        :param str parameters: the parameters to add in the URL.
        :param str headers: request headers.
        :param dict payload: data for POST requests.
        :returns: data or empty :class:`dict` if not found.
        :rtype: :class:`dict` or :class:`List` of :class:`dict`
        '''
        if self._limiter:
            start_time = time.monotonic()
            async with self._limiter:
                end_time = time.monotonic()
                delay_ms = (end_time - start_time) * 1000
                if delay_ms > 10:
                    logger.debug(f"Rate limit introduced delay of {int(delay_ms)}ms.")
                if self.retry:
                    return await self._get_data_async(
                        url, parameters, headers, payload)
                else:
                    # If retry is False, call the underlying method directly
                    return await self._get_data_async.retry_with(
                            stop=stop_after_attempt(1)
                        )(self, url, parameters, headers, payload)
        else: # No limiter configured, proceed directly
            if self.retry:
                return await self._get_data_async(
                    url, parameters, headers, payload)
            else:
                return await self._get_data_async.retry_with(
                        stop=stop_after_attempt(1)
                    )(self, url, parameters, headers, payload)

    @rerun(
        wait=wait_fixed(30),
        retry=retry_if_exception_type(ConnectionRefusedError),
        stop=stop_after_attempt(10)
    )
    async def _get_data_async(
            self,
            url: str,
            parameters: str,
            headers: dict,
            payload: dict = None
    ) -> Union[dict, List[dict]]:

        parameters=parameters.lstrip("&")
        method = 'POST' if payload else 'GET'

        logger.debug(f'HTTP Request: {method} {url}')
        ##logger.debug(f'Headers: {headers}')
        ##logger.debug(f'Payload: {payload}')
        ##logger.debug(f'cURL command: {self._curl_cmd(url, method, headers, payload)}')

        async with httpx.AsyncClient() as client:
            r = await client.request(
                method, url, params=parameters,timeout=self._timeout, headers=headers,
                json=payload)

        data = {}
        if r.status_code == 200:
            data = r.json()
            if len(data) == 1 and 'error' in data:
                data = {}
        elif r.status_code == 400:
            logger.debug('RESPONSE 400')
            data = r.json()
            raise BadQueryParametersException(data['error'])
        elif r.status_code == 403:
            logger.debug('RESPONSE 403')
            raise PermissionError('HTTP status 403 Forbidden.')
        elif r.status_code == 404:
            logger.debug('RESPONSE 404')
            data = r.json()
            raise ObjectNotFoundException(data['error'])
        elif r.status_code == 429:
            logger.debug('RESPONSE 429')
            raise ConnectionRefusedError('HTTP status 429 Too Many Requests.')
        elif r.status_code == 500:
            logger.debug('RESPONSE 500')
            data = r.json()
            raise InternalServerErrorException(data['message'])
        elif r.status_code == 504:
            logger.debug('RESPONSE 504')
            data = r.json()
            raise GatewayTimeoutException(data['message'])

        return data

    def get_data(
                self,
                url: str,
                parameters: str,
                headers: dict,
                payload: dict = None
            ) -> Union[dict, List[dict]]:
        warnings.warn(
            "get_data() is deprecated and will be disabled in the future," +
            " use the async version instead.",
            DeprecationWarning
            )

        # Ensure an event loop is available for the current thread
        try:
            loop = asyncio.get_event_loop_policy().get_event_loop()
            if loop.is_closed(): # Check if the current loop is closed
                raise RuntimeError("Current event loop is closed.")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.get_data_async(
                url=url,
                parameters=parameters,
                headers=headers,
                payload=payload
            )
        )
