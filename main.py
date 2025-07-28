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
    terminals = ['ghostty', 'gnome-terminal', 'konsole', 'xfce4-terminal', 'terminator', 'alacritty', 'kitty', 'xterm']
    
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

def get_resume_command():
    terminal = get_default_terminal()
    claude_path = find_claude_path()
    
    if not claude_path:
        return None
    
    home_dir = os.path.expanduser('~')
    return f'bash -c "cd {home_dir} && {terminal} -e \\"{claude_path} --resume --dangerously-skip-permissions\\""'

def get_terminal_command(argument, dangerous=False):
    terminal = get_default_terminal()
    claude_path = find_claude_path()
    
    if not claude_path:
        return None
    
    home_dir = os.path.expanduser('~')
    dangerous_flag = " --dangerously-skip-permissions" if dangerous else ""
    
    if argument:
        # Properly escape the argument to handle spaces
        escaped_arg = argument.replace('"', '\\"')
        return f'bash -c "cd {home_dir} && {terminal} -e \\"{claude_path}{dangerous_flag} \\\\\\"{escaped_arg}\\\\\\"\\" "'
    else:
        return f'bash -c "cd {home_dir} && {terminal} -e \\"{claude_path}{dangerous_flag}\\""'

class ClaudeTerminalExtension(Extension):

    def __init__(self):
        super(ClaudeTerminalExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        argument = event.get_argument() or ""
        keyword = event.get_keyword()
        
        items = []
        
        # Check if this is the dangerous keyword
        kw_dangerous = extension.preferences.get('kw_dangerous')
        kw_resume = extension.preferences.get('kw_resume')
        is_dangerous = keyword == kw_dangerous
        is_resume = keyword == kw_resume
        
        # Handle resume command specially
        if is_resume:
            cmd = get_resume_command()
        else:
            cmd = get_terminal_command(argument, dangerous=is_dangerous)
        
        if not cmd:
            # Claude not found
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name='Claude Code not found',
                description='Install Claude Code: npm install -g @anthropic-ai/claude-code',
                on_enter=HideWindowAction()
            ))
        elif is_resume:
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name='claude resume (dangerous)',
                description='Resume Claude Code session with dangerous permissions',
                on_enter=RunScriptAction(cmd, [])
            ))
        elif argument:
            dangerous_text = " (dangerous mode)" if is_dangerous else ""
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=f'claude {argument}{dangerous_text}',
                description=f'Launch terminal with "claude {argument}"' + (" with dangerous permissions" if is_dangerous else ""),
                on_enter=RunScriptAction(cmd, [])
            ))
        else:
            dangerous_text = " (dangerous mode)" if is_dangerous else ""
            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=f'claude{dangerous_text}',
                description='Launch terminal with claude code' + (" with dangerous permissions" if is_dangerous else ""),
                on_enter=RunScriptAction(cmd, [])
            ))
        
        return RenderResultListAction(items)

if __name__ == '__main__':
    ClaudeTerminalExtension().run()