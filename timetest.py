from datetime import datetime
import time

current = datetime.now()
print(current.isoformat("T", "seconds"))