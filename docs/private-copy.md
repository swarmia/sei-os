# Make a private copy

Once `company/` holds your goals, metrics and survey results, the repository is an internal handbook. It must be private. GitHub does not allow a fork of a public repository to be private, so create your copy from the template instead.

## Create your copy

1. Open [github.com/swarmia/sei-os](https://github.com/swarmia/sei-os).
2. Click **Use this template** (top right, next to **Code**) → **Create a new repository**.
3. Pick your organization as the owner, name the repository, set visibility to **Private**, and click **Create repository**.

You get a clean history with no link to upstream.

## Pulling upstream updates

Upstream changes `knowledge/`, `skills/`, `shared/`, `scripts/` and `docs/`. It only ever ships templates in `company/`, so your content there is not overwritten unless you also changed a template's structure.

```bash
git remote add upstream https://github.com/swarmia/sei-os.git   # once
git fetch upstream
git merge upstream/main          # add --allow-unrelated-histories the first time
python3 scripts/sync_shared.py   # re-copy shared files into each skill
python3 scripts/validate.py
```

Resolve conflicts in `company/` in favour of your version. Conflicts under `skills/*/references/` or `skills/*/assets/` are generated files: take either side, then re-run `sync_shared.py`.

## Contributing back

Improvements to skills, scripts or `knowledge/` are welcome upstream. Open the pull request from a branch based on `upstream/main` that contains no `company/` changes, never from your private copy's `main`. See [CONTRIBUTING.md](../CONTRIBUTING.md).
