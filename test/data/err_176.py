from datetime import datetime, timezone
import datetime as dt

# Should warn:
start_date = datetime.utcnow()
old_date = datetime.utcfromtimestamp(1)
start_date = dt.datetime.utcnow()
old_date = dt.datetime.utcfromtimestamp(1)

# Should not warn:
start_date = datetime.now(tz=timezone.utc)
old_date = datetime.fromtimestamp(1, tz=timezone.utc)
