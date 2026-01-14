# GenomeMCP Packaging

Templates and manifests for distributing GenomeMCP across platforms.

## Directory Structure

```
packaging/
├── homebrew/
│   └── genomemcp.rb      # Homebrew formula (macOS/Linux)
├── scoop/
│   └── genomemcp.json    # Scoop manifest (Windows)
└── README.md             # This file
```

## Setting Up Distribution

### 1. PyPI (Primary)

Already configured via `.github/workflows/publish.yml`.

1. Create account at [pypi.org](https://pypi.org)
2. Enable trusted publishing for `nexisdev/GenomeMCP`
3. Create a release tag: `git tag v0.1.0 && git push --tags`

### 2. Homebrew Tap

1. Create repo: `github.com/nexisdev/homebrew-genomemcp`
2. Copy `homebrew/genomemcp.rb` to `Formula/genomemcp.rb`
3. Update SHA256 hashes from PyPI

Users install with:

```bash
brew tap nexisdev/genomemcp
brew install genomemcp
```

### 3. Scoop Bucket

1. Create repo: `github.com/nexisdev/scoop-genomemcp`
2. Copy `scoop/genomemcp.json` to `bucket/genomemcp.json`
3. Update SHA256 from release

Users install with:

```powershell
scoop bucket add genomemcp https://github.com/nexisdev/scoop-genomemcp
scoop install genomemcp
```

### 4. Standalone Binaries

Automatically built via `.github/workflows/release.yml` on each tag.
