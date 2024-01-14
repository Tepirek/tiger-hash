class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Writer:
    @staticmethod
    def success(msg: str, before: str = '') -> None:
        print(f'{Colors.HEADER}{before}{Colors.END}{Colors.GREEN}{msg}{Colors.END}')

    @staticmethod
    def error(msg: str, before: str = '') -> None:
        print(f'{Colors.HEADER}{before}{Colors.END}{Colors.FAIL}{msg}{Colors.END}')

    @staticmethod
    def info(msg: str, before: str = '') -> None:
        print(f'{Colors.HEADER}{before}{Colors.END}{msg}')
