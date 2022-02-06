
import os
import sys
from termcolor import colored
from halo import Halo
from .gopher_git_utils import GopherGitUtils
from .gopher_git_printer import GopherGitPrinter


class GopherGit:
    def __init__(self, projects_path: str = None, projects_collect_strategy: str = 'all'):
        self._projects_path: str = projects_path if projects_path else os.getcwd()
        self._projects_collect_strategy: str = projects_collect_strategy
        self._git_projects: list[dict] = []
        self._verify_inputs(self._projects_path, self._projects_collect_strategy)

    @staticmethod
    def get_strategy_descriptions() -> dict:
        return {
            'all': 'returns a summary of all Git projects found in given parent search directory',
            'changed': 'returns only Git projects in which a change was detected (i.e. modified and untracked files)',
            'latest': 'returns all Git projects ignoring changes '
                      '(i.e. useful for getting basic project information such as latest commit)'
        }

    @staticmethod
    def strategy_descriptions_to_colored_str() -> str:
        message = ''
        for strategy, description in GopherGit.get_strategy_descriptions().items():
            message = message + f'\n\t{colored(strategy, color="yellow")}: {description}'
        return message + '\n'

    @staticmethod
    def strategy_description_summary() -> str:
        return f'  Project Search Strategy options are: {GopherGit.get_strategy_types()}\n' \
               f'{GopherGit.strategy_descriptions_to_colored_str()}'

    @staticmethod
    def get_strategy_types() -> list[str]:
        return list(GopherGit.get_strategy_descriptions().keys())

    @staticmethod
    def _verify_inputs(files_path: str, strategy: str) -> None:
        strategy_types: list[str] = GopherGit.get_strategy_types()
        if not os.path.isdir(files_path):
            sys.exit(f'\n  File path given, "{files_path}", is not a valid path\n')
        elif strategy not in strategy_types:
            sys.exit(f'\n  File path "{files_path}" is valid, but project search strategy "{strategy}" was not.\n'
                     f'{GopherGit.strategy_description_summary()}')

    def _collect_git_projects(self) -> list[dict]:
        try:
            git_projects: list[dict] = GopherGitUtils.get_git_projects(self._projects_path)
            for git_project in git_projects:
                git_status: dict = GopherGitUtils.get_git_status(
                    git_project["directory_path"],
                    self._projects_collect_strategy
                )
                git_latest_commit: dict = GopherGitUtils.get_latest_git_commit_summary(git_project["directory_path"])
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
            spinner = Halo(text='Collecting Git Projects...', spinner='dots')
            spinner.start()
            collected_projects: list[dict] = self._collect_git_projects()
            spinner.stop()
            GopherGitPrinter.print_to_terminal(
                self._projects_path,
                collected_projects,
                self._projects_collect_strategy
            )
            sys.exit()
        except Exception as error:
            print(f'Received Exception: {error}')


def print_terminal_help():
    strategy_param_display: str = colored('project_search_strategy', color='yellow')
    parent_directory_display: str = colored('projects_parent_directory', color='yellow')
    print(f'\nUsage: gogit [-h output usage] <{strategy_param_display}> <{parent_directory_display}>\n\n'
          f'Defaults given no params:\n'
          f'   <{parent_directory_display}> = current calling directory\n'
          f'   <{strategy_param_display}> = "all" \n')
    print(f'{GopherGit.strategy_description_summary()}')


def terminal_main() -> None:
    try:
        spinner = Halo(text='Loading', spinner='dots')
        spinner.start()
        if len(sys.argv) == 1:
            gopher_git_job = GopherGit()
            gopher_git_job.terminal_run()
        elif len(sys.argv) == 2:
            if '-h' in sys.argv[1]:
                print_terminal_help()
            else:
                gopher_git_job = GopherGit(None, sys.argv[1])
                gopher_git_job.terminal_run()
        elif len(sys.argv) == 3:
            gopher_git_job = GopherGit(sys.argv[2], sys.argv[1])
            gopher_git_job.terminal_run()
        else:
            print_terminal_help()

    except TypeError as error:
        print(f'Received TypeError: {error}')
        sys.exit()
