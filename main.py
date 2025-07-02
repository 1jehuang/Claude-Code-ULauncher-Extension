import subprocess
import logging
import os
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

logger = logging.getLogger(__name__)

def get_default_terminal():
    terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'terminator', 'alacritty', 'kitty', 'xterm']
    
    for terminal in terminals:
        if subprocess.run(['which', terminal], capture_output=True).returncode == 0:
            return terminal
    
    return 'xterm'

def find_claude_path():
    """Find Claude Code installation path"""
    possible_paths = [
        # Global npm installations
        os.path.expanduser('~/.npm-global/bin/claude'),
        '/usr/local/bin/claude',
        '/usr/bin/claude',
        # Local npm installations
        os.path.expanduser('~/.local/bin/claude'),
        # Check if it's in PATH
        'claude'
    ]
    
    for path in possible_paths:
        if path == 'claude':
            # Check if claude is in PATH
            try:
                result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                continue
        else:
            # Check if file exists and is executable
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
    
    return None

def get_terminal_command(argument):
    terminal = get_default_terminal()
    claude_path = find_claude_path()
    
    if not claude_path:
        return None
    
    home_dir = os.path.expanduser('~')
    if argument:
        # Properly escape the argument to handle spaces
        escaped_arg = argument.replace('"', '\\"')
        return f'bash -c "cd {home_dir} && {terminal} -- {claude_path} \\"{escaped_arg}\\""'
    else:
        return f'bash -c "cd {home_dir} && {terminal} -- {claude_path}"'

class ClaudeTerminalExtension(Extension):

    def __init__(self):
        super(ClaudeTerminalExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        argument = event.get_argument() or ""
        
        items = []
        
        cmd = get_terminal_command(argument)
        
        if not cmd:
            # Claude not found
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name='Claude Code not found',
                description='Install Claude Code: npm install -g @anthropic-ai/claude-code',
                on_enter=HideWindowAction()
            ))
        elif argument:
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=f'claude {argument}',
                description=f'Launch terminal with "claude {argument}"',
                on_enter=RunScriptAction(cmd, [])
            ))
        else:
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name='claude',
                description='Launch terminal with claude code',
                on_enter=RunScriptAction(cmd, [])
            ))
        
        return RenderResultListAction(items)

if __name__ == '__main__':
    ClaudeTerminalExtension().run()