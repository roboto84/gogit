
from termcolor import colored
from .gopher_git_utils import GopherGitUtils


class GopherGitPrinter:
    @staticmethod
    def print_git_project_summary(project_name: str, git_branch: str, git_log: dict, branch_status: str,
                                  branch_state_comparator: bool, project_path: str, modified_files: list[str],
                                  untracked_files: list[str]):
        project_name = colored(f' {project_name} ', 'white', 'on_cyan')
        git_branch: str = colored(f'{git_branch}', 'cyan')

        print(f'{project_name}')
        print(f'  {git_branch} {project_path}')
        if branch_state_comparator:
            print(f'  {branch_status}')
        print(f'  Last Commit {GopherGitPrinter.latest_git_commit_to_str(git_log)}')
        GopherGitPrinter.print_modified_files(modified_files)
        GopherGitPrinter.print_untracked_files(untracked_files)
        print('')

    @staticmethod
    def print_modified_files(modified_files: list[str]) -> None:
        if len(modified_files):
            print(f'\n  Changes (staged and non-staged):')
            for modified_file in modified_files:
                split_output_text: list[str] = modified_file.split(':')
                modified_file_name: str = colored(f'{split_output_text[1].strip()}', 'yellow')
                print(f'{split_output_text[0]}: {modified_file_name}')

    @staticmethod
    def print_untracked_files(untracked_files: list[str]) -> None:
        if len(untracked_files):
            print(f'\n  Untracked Files:')
            for untracked_file in untracked_files:
                file_name: str = colored(f' {untracked_file} ', 'yellow')
                print(f'{file_name}')

    @staticmethod
    def latest_git_commit_to_str(latest_commit: dict) -> str:
        return f'{latest_commit["commit_author"]} - {colored(latest_commit["commit_hash"], "magenta")} ' \
               f'({latest_commit["commit_date"]}): {latest_commit["commit_message"]}'

    @staticmethod
    def print_to_terminal(projects_path: str, git_projects: list[dict], projects_collect_strategy):
        try:
            print('')
            if len(git_projects) > 0:
                for git_project in git_projects:
                    _projects_comparator: bool = True

                    if GopherGitUtils.is_strategy_collect_changed_projects(projects_collect_strategy):
                        _projects_comparator = git_project['git_status']['has_project_got_changes']

                    if _projects_comparator:
                        GopherGitPrinter.print_git_project_summary(
                            git_project['git_project_details']['directory_name'],
                            git_project['git_status']['project_branch'],
                            git_project['git_latest_commit'],
                            git_project['git_status']['project_branch_status'],
                            git_project['git_status']['has_branch_changed'],
                            git_project['git_project_details']['directory_path'],
                            git_project['git_status']['modified_files'],
                            git_project['git_status']['untracked_files']
                        )
            else:
                print(f'  No Git projects found in "{projects_path}"\n')
        except TypeError as type_error:
            print(f'Received TypeError: {type_error}')
