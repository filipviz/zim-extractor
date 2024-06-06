# zim-extract

`zim-extract` allows you to take one or more `.zim` files, like the Wiki dumps from [kiwix](https://kiwix.org/), extract their content, and prepare them for an LLM to use.

1. Take a [`.zim`](https://en.wikipedia.org/wiki/ZIM_(file_format)) file.
2. Extract text from each item using [Trafilatura](https://trafilatura.readthedocs.io/en/latest/).
3. De-duplicate on a document level using SimHash.
