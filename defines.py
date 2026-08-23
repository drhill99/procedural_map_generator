from colorama import init, Fore, Back, Style

WALL = f"{Fore.BLACK}{Back.LIGHTBLACK_EX}#{Style.RESET_ALL}"
DELETED = f"{Fore.RED}D{Style.RESET_ALL}"
EXPANDED = f"{Fore.GREEN}E{Style.RESET_ALL}"
NEW = f"{Fore.MAGENTA}N{Style.RESET_ALL}"
FLOOR = f"{Fore.LIGHTWHITE_EX}{Back.BLACK}+{Style.RESET_ALL}"
ENDPOINT = "E"