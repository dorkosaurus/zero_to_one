#!/usr/bin/env bash
set -euo pipefail

# Installer for the ESM3 druggability pipeline.
# Run with: make install   (which calls this script)

P2RANK_VERSION="${P2RANK_VERSION:-2.4.2}"
P2RANK_DIR="${P2RANK_DIR:-$HOME/tools/p2rank}"
VENV="${VENV:-$HOME/venv}"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(uname -s)" != "Linux" ]]; then
    echo "This installer targets Linux (Ubuntu/Debian). Detected: $(uname -s)" >&2
    exit 1
fi

echo "==> 1/4: apt packages (build deps, OpenJDK, wget) + fpocket from source"
sudo apt-get update
sudo apt-get install -y build-essential git default-jre wget ca-certificates

if command -v fpocket >/dev/null 2>&1; then
    echo "    fpocket already installed at $(command -v fpocket)"
else
    echo "    Building fpocket from source..."
    # Build under repo (.build/) not /tmp — /tmp is a small tmpfs on this host.
    builddir="$REPO_DIR/.build"
    mkdir -p "$builddir"
    rm -rf "$builddir/fpocket"
    git clone --depth 1 https://github.com/Discngine/fpocket.git "$builddir/fpocket"
    # GCC 14+ (Ubuntu 25.10) promotes incompatible-pointer-types and int-conversion to
    # errors. fpocket's source has legacy issues that hit both. Demote to warnings.
    sed -i 's/^CWARN.*=.*/& -Wno-error=incompatible-pointer-types -Wno-error=int-conversion/' "$builddir/fpocket/makefile"
    make -C "$builddir/fpocket" -j"$(nproc)"
    sudo make -C "$builddir/fpocket" install
    rm -rf "$builddir/fpocket"
fi

echo
echo "==> 2/4: P2Rank ${P2RANK_VERSION} -> ${P2RANK_DIR}"
if [[ -x "$P2RANK_DIR/prank" ]]; then
    echo "    already installed; skipping (delete $P2RANK_DIR to reinstall)"
else
    mkdir -p "$(dirname "$P2RANK_DIR")"
    mkdir -p "$REPO_DIR/.build"
    tmpdir="$(mktemp -d -p "$REPO_DIR/.build")"
    trap 'rm -rf "$tmpdir"' EXIT
    url="https://github.com/rdk/p2rank/releases/download/${P2RANK_VERSION}/p2rank_${P2RANK_VERSION}.tar.gz"
    echo "    fetching $url"
    wget -q -O "$tmpdir/p2rank.tar.gz" "$url" || {
        echo "    download failed; check P2RANK_VERSION (current: $P2RANK_VERSION)" >&2
        exit 1
    }
    tar -xzf "$tmpdir/p2rank.tar.gz" -C "$tmpdir"
    mv "$tmpdir/p2rank_${P2RANK_VERSION}" "$P2RANK_DIR"
fi

echo
echo "==> 3/4: Python deps into $VENV"
if [[ ! -f "$VENV/bin/activate" ]]; then
    echo "    ERROR: expected venv at $VENV. Create it first: python3 -m venv $VENV" >&2
    exit 1
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install --upgrade pip
pip install -e "$REPO_DIR"

echo
echo "==> 4/4: verification"
ok=1
if command -v fpocket >/dev/null 2>&1; then
    echo "    fpocket: $(fpocket -v 2>&1 | head -n1 || echo found)"
else
    echo "    fpocket: MISSING" >&2; ok=0
fi
if [[ -x "$P2RANK_DIR/prank" ]]; then
    echo "    P2Rank:  $P2RANK_DIR/prank"
else
    echo "    P2Rank:  MISSING" >&2; ok=0
fi
if python -c "import requests, dotenv, Bio, pandas, numpy, sklearn, tqdm" 2>/dev/null; then
    echo "    Python:  all deps importable"
else
    echo "    Python:  some deps failed to import" >&2; ok=0
fi

echo
if [[ "$ok" -eq 1 ]]; then
    echo "Install complete."
    echo "Add P2Rank to PATH if you want bare 'prank' calls:"
    echo "  export PATH=\"$P2RANK_DIR:\$PATH\""
else
    echo "Install finished with issues — see messages above." >&2
    exit 1
fi
