print("main!")

from .config import read_from_toml
from .utils import check_for_git_changes

def main():
    print("Changes?")
    print(check_for_git_changes())


if __name__ == "__main__":
    main()