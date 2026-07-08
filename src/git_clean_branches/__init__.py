"""
git-clean-branches - a clean-up tool for Git branches.

Th app deletes local Git branches those are "gone"
i.e. pointing to non-existing remote branch.
"""

import sys
from argparse import ArgumentParser

from plumbum import ProcessExecutionError, local
from plumbum.cli.terminal import ask
from plumbum.colors import warn  # ty: ignore[unresolved-import]

git = local["git"]


class App:
    """
    A main application class.

    It exposes an entry-point and contains all the app's logic.
    """

    cli = ArgumentParser(
        "git-clean-branches", description=('Deletes Git branches those are "gone"'),
    )
    cli.add_argument("--fetch", action="store_true", help=("do 'git fetch' first"))
    cli.add_argument(
        "-D",
        "--force-delete",
        action="store_true",
        help=("delete Git branches forcefully (call 'git branch -D')"),
    )

    do_fetch: bool
    gone_branches: list[str]
    branch_map: dict[int, str]
    selected: list[int]
    do_delete: bool
    force_delete: bool

    @classmethod
    def main(cls) -> None:
        """
        Run the App.

        An entry-point for scripts.
        """
        app = cls()
        app._parse_cli()
        app._require_remote()
        app._fetch()
        app._collect_gone_branches()
        app._enumerate_and_print_branches()
        app._select_branches()
        app._confirm_deletion()
        app._delete_selected()

    def _parse_cli(self):
        options = self.cli.parse_args()
        self.do_fetch = options.fetch
        self.force_delete = options.force_delete

    def _require_remote(self):
        try:
            remotes = git["remote"]()
        except ProcessExecutionError:
            print("Non-Git repo or something got wrong.")
            sys.exit(1)

        if not remotes.split():
            print("Can't clean anything because no remotes found.")
            sys.exit(2)

    def _fetch(self):
        if self.do_fetch:
            try:
                git["fetch", "--prune"]()
            except ProcessExecutionError:
                print("Can't fetch the remote.")
                sys.exit(3)

    def _collect_gone_branches(self):
        try:
            branches = git["branch", "-vv"]()
        except ProcessExecutionError:
            print("Can't list local branches.")
            sys.exit(4)
        self.gone_branches = [
            b.split(maxsplit=1)[0]
            for b in branches.split("\n")
            if ": gone" in b
        ]

    def _enumerate_and_print_branches(self):
        print("These branches are \"gone\" (don't have remotes anymore):\n")
        self.branch_map = dict[int, str]()
        for i, b in enumerate(self.gone_branches, start=1):
            self.branch_map[i] = b
            print(f"{i:d}) {b}")
        print()


    def _select_branches(self):
        typed = input(
            "Choose branches to delete "
            "(comma-separated numbers, empty means ALL):",
        )
        if typed:
            self.selected = sorted(
                k for k in (int(s) for s in typed.split(","))
                if k in self.branch_map
            )
        else:
            self.selected = sorted(self.branch_map.keys())


    def _confirm_deletion(self):
        print(warn | "\nThese LOCAL branches will be DELETED:\n")
        for k in self.selected:
            print(warn | self.branch_map[k])
        print()
        self.do_delete = ask("Continue", default=True)

    def _delete_selected(self):
        deletion_mode = "-D" if self.force_delete else "d"
        if self.do_delete:
            for k in self.selected:
                b = self.branch_map[k]
                try:
                    git["branch", deletion_mode, b]()
                except ProcessExecutionError:
                    print(f"Can't delete the branch '{b}'")
        else:
            print("Aborted")


main = App.main
