from .instance import DflyInstance
from . import dfly_args
from meta_memcache import (
    Key,
    ServerAddress,
    CacheClient,
    connection_pool_factory_builder,
)
from meta_memcache.protocol import RequestFlags, Success

DEFAULT_ARGS = {"memcached_port": 11211, "proactor_threads": 4}


@dfly_args(DEFAULT_ARGS)
def test_basic(df_server: DflyInstance):
    pool = CacheClient.cache_client_from_servers(
        servers=[
            ServerAddress(host="localhost", port=DEFAULT_ARGS.get("memcached_port")),
        ],
        connection_pool_factory_fn=connection_pool_factory_builder(recv_timeout=5),
    )

    assert pool.set("key1", "value1", 100)
    assert pool.set("key1", "value2", 0)
    assert pool.get("key1") == "value2"

    request_flags = RequestFlags(return_value=False)
    response = pool.meta_get(Key("key1"), flags=request_flags)
    assert isinstance(response, Success)
    assert pool.get("key2") is None
    assert pool.delete("key1")
    assert pool.delete("key1") is False

    assert pool.set("cask", "v", 100)
    value, cas_token = pool.get_cas("cask")
    assert value == "v" and cas_token == 0

    k = Key("cask")
    response = pool.meta_multiget([k], RequestFlags(return_cas_token=True, return_value=True))
    assert k in response
    assert response[k].flags.cas_token == 0 and response[k].value == "v"
