# Claude Code Launcher for Ulauncher

A simple Ulauncher extension to quickly launch Claude Code terminal sessions.

## Features

- Launch Claude Code in your default terminal with a simple keyword
- Pass arguments directly: `k test` runs `claude test`
- Handles arguments with spaces: `k what is my default terminal`
- Automatically detects Claude Code installation path
- Starts Claude in your home directory
- Works with any terminal (gnome-terminal, kitty, alacritty, etc.)

## Prerequisites

- [Ulauncher](https://ulauncher.io/) installed
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed

Install Claude Code:
```bash
npm install -g @anthropic-ai/claude-code
```

## Installation

1. Clone this repository to your Ulauncher extensions directory:
```bash
git clone https://github.com/jeremy/claude-code-ulauncher ~/.local/share/ulauncher/extensions/com.github.jeremy.claude-kitty
```

2. Restart Ulauncher or reload extensions

## Usage

- Open Ulauncher (default: Alt+Space)
- Type `k` to launch Claude Code
- Type `k <your question>` to launch Claude with a specific prompt

Examples:
- `k` - Opens Claude Code in terminal
- `k test` - Opens Claude with "test" as argument
- `k what is my default terminal` - Opens Claude with full question

## Configuration

The extension uses the keyword `k` by default. You can change this in Ulauncher preferences.

## How it works

The extension automatically detects your Claude Code installation by checking:
- `~/.npm-global/bin/claude`
- `/usr/local/bin/claude`
- `/usr/bin/claude`
- `~/.local/bin/claude`
- System PATH

It launches your default terminal and starts Claude in your home directory.

## License

MIT License