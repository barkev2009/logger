# logger
Logger with a progress bar, able to estimate time left until task completion, write logs to .txt and console in a readable manner and work in multiple threads

# 1. Initiating the logger
Just add a line: 
`logger = Logger(items)`
where variable `items` is a list of items you want to go through in your code (links, images, strings, variables etc.). Further guide will consider a list of links to parse as an example.

You can alter the length of the progress bar by adding an attribute `logger = Logger(items, progress_bar_length=30)`

# 2. Logging information
To add one line of log info use `logger.log(info)`. Be careful to log exactly one line at a time, to log multiple lines use multiple log commands.

If you want to use logger in multiple threads, initilize logger in the main thread, then pass your logger and a thread ID into your target function and use `logger.log(info, thread_id)` to log into multiple threads correctly.

# 3. Indicating item processing
To explicitly tell the logger to move forward, use `logger.item_processed()` (or `logger.item_processed(thread_id)` for multi-threading cases) after you are done with the item.

For example: when looping over a list of links to parse, add a line `logger.item_processed()` (or `logger.item_processed(thread_id)` for multi-threading cases) after you have parsed the link. Otherwise the logger will prevent your program from proper completion.

# 4. End logging
When the logger has gone through all the items, use command `logger.end_logging()` to stop the logger correctly. 

You can alter flags `log_to_txt` and `log_to_console` according to your needs. Flags `log_to_txt=False` and `log_to_console=True` are set by default.
