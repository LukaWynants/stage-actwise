
sc.exe config TrustedInstaller binpath= "C:\Windows\servicing\TrustedInstaller.exe"

Install-Module -Name NtObjectManager -RequiredVersion 1.1.32 -Force

Set-ExecutionPolicy Bypass -Scope LocalMachine -Force
Import-Module NtObjectManager

Start-Service TrustedInstaller

$p = Get-NtProcess TrustedInstaller.exe
$th = $p.GetFirstThread()
$current = Get-NtThread -Current -PseudoHandle
$imp = $current.ImpersonateThread($th)
$imp_token = Get-NtToken -Impersonation
$imp_token.groups