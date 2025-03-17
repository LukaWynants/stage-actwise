sc.exe config TrustedInstaller binpath= "C:\Windows\servicing\TrustedInstaller.exe" #set default
Restart-Service TrustedInstaller
Install-Module -Name NtObjectManager -RequiredVersion 1.1.32 #install 
Import-Module NtObjectManager

sc.exe start TrustedInstaller
$p = Get-NtProcess TrustedInstaller.exe
$process = New-Win32Process cmd.exe -CreationFlags NewConsole -ParentProcess $p #spawn a powershell with trustedinstaller access