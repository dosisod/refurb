from typing import cast

# Due to how Mypy's default traverser works, this expression will emit 2
# errors instead of just one. This is fixed now, and should only return 1
# error.

cast(int, int(0))
