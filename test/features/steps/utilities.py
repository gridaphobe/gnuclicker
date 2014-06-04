"""
We place various misc functions here.


"""
import time

HOSTNAME = 'localhost:5000'




def wait_for_webpage_to_load(context, timeout=20):
    start_time = time.time()
    while time.time() - start_time <= timeout:
        time.sleep(0.5)
        if 'complete' == context.browser.execute_script('return document.readyState'):
            return
    assert False # timeout
