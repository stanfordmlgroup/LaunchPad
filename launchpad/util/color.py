class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def colorful_state(state):
    if state == "Running":
        return f"{Colors.OKGREEN}Running{Colors.ENDC}"
    elif state == "Pending":
        return f"{Colors.OKBLUE}Pending{Colors.ENDC}"
    elif state == "Finished":
        return f"{Colors.WARNING}Finished{Colors.ENDC}"
    elif state == "Compiled":
        return f"{Colors.BOLD}Compiled{Colors.ENDC}"
    else:
        return f"{Colors.FAIL}Unknown{Colors.ENDC}"


