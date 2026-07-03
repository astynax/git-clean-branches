# git-clean-branches

Are you using Git with feature branches, merge them amd delete them on the remote side?

Are you tired from the orphan feature branches those you still have locally but those are already merged and deleted from the `origin`?

Then you may find helpful this simple app. All that it does is automating of

- `git fetch --prune`
- `git branch -vv` + `grep ": gone]"`
- `git branch -d <NAME>` for each branch that you choose from the "gone" ones

Enjoy!
