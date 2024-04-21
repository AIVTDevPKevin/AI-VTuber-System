import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import inspect










def aprint(print_content, start=""):
    print(print_content)
    '''
    filename = os.path.basename(sys.argv[0])
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame, 2)
    function_name = caller_frame[1][3]
    print(f"{start}{filename} | {function_name} - {print_content}")
    '''




