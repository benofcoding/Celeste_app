
# from datetime import datetime, timedelta


# epoch_1980 = datetime(1980, 1, 1)
# print(epoch_1980, timedelta(seconds=8000)
# )

import datetime

# Get today's date
today = datetime.date.today()

# Define the 1980-01-01 epoch
epoch = datetime.date(1980, 1, 1)

# Calculate difference in days and convert to seconds
seconds_since_1980 = int((today - epoch).total_seconds())

print(seconds_since_1980)