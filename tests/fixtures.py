import pytest
import aiohttp
from unittest.mock import AsyncMock


@pytest.fixture
def aiohttp_response():
    def create_response(*args, **kwargs): 
        mock = AsyncMock(spec=aiohttp.ClientResponse)

        for key, value in kwargs.items():
            setattr(mock, key, value)
        
        return mock

    return create_response
