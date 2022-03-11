# HBSC Chia Python utils

A collection of Python utils to make Chia development easier.

## RPC clients

Chia RPC clients are implemented as context managers, and extendable:

Use them like:
```python
from hbsc_utils.rpc import ChiaFullNodeWrapper

async with ChiaFullNodeWrapper() as (wrapper, client):
    await client.do_stuff()  # this is the underlying Chia RPC client, with all the documented methods
    await wrapper.do_stuff()  # this is our custom wrapper which might have additional features
```

You can pass in your own hostname and port, or set the following environment variables:

```
CHIA_FULL_NODE_HOSTNAME
CHIA_FULL_NODE_PORT
CHIA_WALLET_HOSTNAME
CHIA_WALLET_PORT
```

### Get CAT original XCH address
Need to send more of a CAT to someone?

```python
async with ChiaFullNodeWrapper() as (wrapper, client):
    cat_record = await client.get_coin_record_by_name(COIN_ID)
    xch_address = await wrapper.get_original_address_for_cat(cat_record, CAT_TAIL)

    # send CAT to xch_address
```


## Contributing
Feel free to contribute anything but please open an issue first.

Want to say thanks? `xch18csq9v42nvmdwckkte2cke8vdmrv7ew8xqtqdswyult29gk5p7eqv95nge`
