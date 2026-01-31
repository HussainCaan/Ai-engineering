from langchain_community.tools import ShellTool
# from langchain_community import langchain_experimental
shell_tool = ShellTool()

# Execute a shell command
command = input("Enter a shell command to execute: ")

output = shell_tool.invoke(command)
print("Command Output:")
print(output)