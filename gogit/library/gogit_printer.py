
from datetime import timedelta
from termcolor import colored
from .gogit_utils import GogitUtils


class GogitPrinter:
    @staticmethod
    def print_git_project_summary(project_name: str, git_branch: str, git_log: dict, branch_status: str,
                                  branch_state_comparator: bool, project_path: str, modified_files: list[dict],
                                  untracked_files: list[dict]):
        project_name = colored(f' {project_name} ', 'white', 'on_cyan')
        git_branch: str = colored(f'{git_branch}', 'cyan')

        print(f'{project_name}')
        print(f'  {git_branch} {project_path}')
        if branch_state_comparator:
            print(f'  {branch_status}')
        print(f'  {GogitPrinter.latest_git_commit_to_str(git_log)}')
        GogitPrinter.print_modified_files(modified_files)
        GogitPrinter.print_untracked_files(untracked_files)
        print('')

    @staticmethod
    def print_modified_files(modified_files: list[dict]) -> None:
        if len(modified_files):
            print(f'\n  Changes (staged and non-staged):')
            for modified_file in modified_files:
                modified_file_name: str = colored(f'{modified_file["file_name"]}', 'yellow')
                print(f'\t{(modified_file["long_type"]+":").ljust(11, " ")} {modified_file_name}')

    @staticmethod
    def print_untracked_files(untracked_files: list[dict]) -> None:
        if len(untracked_files):
            print(f'\n  Untracked Files:')
            for untracked_file in untracked_files:
                file_name: str = colored(f'\t{untracked_file["file_name"]} ', 'red')
                print(f'{file_name}')

    @staticmethod
    def time_delta_to_str(time_delta: timedelta) -> tuple[int, str]:
        week_divisor: int = 7
        month_divisor: int = 4
        year_divisor: int = 12
        time_delta_hours_estimate: int = int(time_delta.total_seconds()/(60*60*24))
        time_word: str = 'days' if time_delta_hours_estimate > 1 else 'day'

        if time_delta_hours_estimate > week_divisor:
            time_delta_hours_estimate = int(time_delta_hours_estimate/week_divisor)
            time_word = 'weeks' if time_delta_hours_estimate > 1 else 'week'
        if time_delta_hours_estimate > month_divisor:
            time_delta_hours_estimate = int(time_delta_hours_estimate/month_divisor)
            time_word = 'months' if time_delta_hours_estimate > 1 else 'month'
        if time_delta_hours_estimate > year_divisor:
            time_delta_hours_estimate = int(time_delta_hours_estimate/year_divisor)
            time_word = 'years' if time_delta_hours_estimate > 1 else 'year'
        return time_delta_hours_estimate, time_word

    @staticmethod
    def latest_git_commit_to_str(latest_commit: dict) -> str:
        if latest_commit:
            latest_commit_time_delta: tuple = GogitPrinter.time_delta_to_str(latest_commit["time_since_commit"])
            colored_time_delta: str = colored(
                f'{latest_commit_time_delta[0]} {latest_commit_time_delta[1]} ago',
                attrs=['bold']
            )
            colored_author: str = colored(latest_commit["commit_author"], attrs=["bold"])
            return f'Latest {colored_time_delta} by {colored_author} ' \
                   f'({latest_commit["commit_date"].strftime("%m/%d/%Y %H:%M")}) ' \
                   f'{colored(latest_commit["commit_hash"], "magenta")}: ' \
                   f'{latest_commit["commit_message"]}'
        else:
            return 'Current branch does not have any commits yet'

    @staticmethod
    def print_to_terminal(projects_path: str, git_projects: list[dict], projects_collect_strategy):
        try:
            print('')
            if len(git_projects) > 0:
                for git_project in git_projects:
                    projects_comparator: bool = True

                    if GogitUtils.is_strategy_collect_changed_projects(projects_collect_strategy):
                        projects_comparator = git_project['git_status']['has_project_got_changes']

                    if projects_comparator:
                        GogitPrinter.print_git_project_summary(
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
