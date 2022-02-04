
import os
import sys
from .library.gopher_git_utils import GopherGitUtils
from .library.gopher_git_printer import GopherGitPrinter


class GopherGit:
    def __init__(self, projects_path: str, projects_collect_strategy: str):
        self._projects_path: str = projects_path
        self._projects_collect_strategy: str = projects_collect_strategy
        self._git_projects: list[dict] = []
        self._verify_inputs(self._projects_path, self._projects_collect_strategy)

    @staticmethod
    def _get_strategy_types() -> list[str]:
        return ['all', 'changed']

    @staticmethod
    def _verify_inputs(files_path: str, strategy: str) -> None:
        strategy_types: list[str] = GopherGit._get_strategy_types()
        if not os.path.isdir(files_path):
            sys.exit(f'\n  File path given, "{files_path}", is not a valid path\n')
        elif strategy not in strategy_types:
            sys.exit(f'\n  File path is valid, but project search strategy was not.\n'
                     f'  Project Search Strategy options are: {strategy_types}\n')

    def _collect_git_projects(self) -> list[dict]:
        try:
            git_projects: list[dict] = GopherGitUtils.get_git_projects(self._projects_path)
            for git_project in git_projects:
                git_latest_commit: dict = GopherGitUtils.get_latest_git_commit_summary(git_project["directory_path"])
                git_status: dict = GopherGitUtils.get_git_status(git_project["directory_path"])
                self._git_projects.append({
                    'git_project_details': git_project,
                    'git_latest_commit': git_latest_commit,
                    'git_status': git_status
                })
            return self._git_projects
        except TypeError as type_error:
            print(f'Received TypeError: {type_error}')

    def terminal_run(self) -> None:
        try:
            GopherGitPrinter.print_to_terminal(
                self._projects_path,
                self._collect_git_projects(),
                self._projects_collect_strategy
            )
            sys.exit()
        except Exception as error:
            print(f'Received Exception: {error}')


def terminal_main() -> None:
    try:
        if len(sys.argv) == 3:
            gopher_git_job = GopherGit(sys.argv[1], sys.argv[2])
            gopher_git_job.terminal_run()
        else:
            print('\nUsage: gogit [-h output usage] <projects_parent_directory> <project_search_strategy>\n\n'
                  'Both <projects_parent_directory> and <project_search_strategy> params are needed\n')

    except TypeError as error:
        print(f'Received TypeError: {error}')
        sys.exit()


if __name__ == '__main__':
    terminal_main()
