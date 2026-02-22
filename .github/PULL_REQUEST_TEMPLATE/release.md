## Release PR

### Checklist (required)

- [ ] `make bump-patch` / `make bump-minor` / `make bump-major` を実行し、version を更新した
- [ ] `CHANGELOG.md` に今回の version 見出しを追加した
- [ ] `make release-check` を実行して成功した
- [ ] （可能なら）`make e2e-claude` も成功した
- [ ] タグ予定名 (`vX.Y.Z`) と `make version` が一致している

### Release Notes Draft

- Added:
- Changed:
- Fixed:

### Risk / Rollback

- Risk:
- Rollback plan:
