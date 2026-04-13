#!/usr/bin/env python3
"""Update all git tools to use color highlighting."""

import re

def update_git_tools():
    with open('lunvex_code/tools/git_tools.py', 'r') as f:
        content = f.read()
    
    # Find all execute methods and update them
    pattern = r'(def execute\(.*?\) -> ToolResult:.*?\n        git_result = self\._run_git_command\(args\)\n        output = self\._format_output\(git_result, format\))'
    
    def replace_execute(match):
        execute_block = match.group(1)
        
        # Extract tool name from class definition
        # Look backward for class definition
        start_pos = match.start()
        class_start = content.rfind('class ', 0, start_pos)
        if class_start != -1:
            class_line_end = content.find('\n', class_start)
            class_line = content[class_start:class_line_end]
            # Extract class name
            class_match = re.search(r'class (\w+)', class_line)
            if class_match:
                class_name = class_match.group(1)
                # Convert class name to tool name (e.g., GitStatusTool -> git_status)
                tool_name = re.sub(r'([a-z])([A-Z])', r'\1_\2', class_name).lower().replace('_tool', '')
                
                # Add tool_name parameter
                execute_block = execute_block.replace(
                    'output = self._format_output(git_result, format)',
                    f'output = self._format_output(git_result, format, tool_name=self.name)'
                )
        
        return execute_block
    
    # Update all execute methods
    new_content = re.sub(pattern, replace_execute, content, flags=re.DOTALL)
    
    # Also update specific tools that need additional parameters
    # GitStatusTool needs short parameter
    new_content = new_content.replace(
        'output = self._format_output(git_result, format, tool_name=self.name)',
        'output = self._format_output(git_result, format, tool_name=self.name, short=short)',
        1  # Only replace first occurrence (GitStatusTool)
    )
    
    # GitLogTool needs oneline parameter
    new_content = new_content.replace(
        '        git_result = self._run_git_command(args)\n        output = self._format_output(git_result, format, tool_name=self.name)\n',
        '        git_result = self._run_git_command(args)\n        output = self._format_output(git_result, format, tool_name=self.name, oneline=oneline)\n',
        1  # Only replace GitLogTool's execute method
    )
    
    with open('lunvex_code/tools/git_tools.py', 'w') as f:
        f.write(new_content)
    
    print("Updated git tools with color highlighting support!")

if __name__ == "__main__":
    update_git_tools()