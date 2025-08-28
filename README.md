# 🎨 Gitch - GitHub Fastfetch

Terminal tool to display GitHub user profiles with ASCII avatars.

## 🚀 Installation

```bash
# Install dependencies
sudo apt install chafa python3-pip  # Ubuntu/Debian
# or: brew install chafa python3     # macOS

pip install blessed requests

```

## 🎯 Usage

```bash
# Random user
./main.py

# Specific user
./main.py octocat

# With GitHub token (recommended)
export GITHUB_TOKEN=your_token
./main.py octocat
```

**Get token:** GitHub.com → Settings → Developer settings → Personal access tokens

