#Requires -RunAsAdministrator
<#
    Configure Windows crash dump collection before you start chasing BSODs.
    Tested on Windows Server 2022 and Windows 11 23H2.

    Run from an elevated PowerShell prompt inside the guest:
        Set-ExecutionPolicy -Scope Process Bypass -Force
        .\windows-crashdump-config.ps1

    Reboot afterwards.
#>

$ErrorActionPreference = 'Continue'
$CrashControl = 'HKLM:\SYSTEM\CurrentControlSet\Control\CrashControl'

Write-Host '== Crash dump settings =='
# 0 none, 1 complete, 2 kernel, 3 small, 7 automatic memory dump
Set-ItemProperty -Path $CrashControl -Name 'CrashDumpEnabled' -Value 7
Set-ItemProperty -Path $CrashControl -Name 'DumpFile' -Value '%SystemRoot%\MEMORY.DMP'
Set-ItemProperty -Path $CrashControl -Name 'MinidumpDir' -Value '%SystemRoot%\Minidump'
Set-ItemProperty -Path $CrashControl -Name 'Overwrite' -Value 1
Set-ItemProperty -Path $CrashControl -Name 'AlwaysKeepMemoryDump' -Value 1
# Keep the stop screen on display instead of rebooting immediately.
Set-ItemProperty -Path $CrashControl -Name 'AutoReboot' -Value 0

Write-Host '== System-managed page file on the system drive =='
# A complete or automatic dump needs a page file on C: large enough to
# stage the dump before it is written to MEMORY.DMP.
$ComputerSystem = Get-CimInstance -ClassName Win32_ComputerSystem
if (-not $ComputerSystem.AutomaticManagedPagefile) {
    Set-CimInstance -InputObject $ComputerSystem -Property @{ AutomaticManagedPagefile = $true }
}

Write-Host '== Allow a manual bugcheck from the console keyboard =='
# Press right Ctrl + Scroll Lock + Scroll Lock in the VNC console to force
# a bugcheck on a hung guest. Both drivers are covered because the keyboard
# may be virtio (kbdhid) or emulated PS/2 (i8042prt).
foreach ($Driver in @('kbdhid', 'i8042prt')) {
    $Params = "HKLM:\SYSTEM\CurrentControlSet\Services\$Driver\Parameters"
    if (-not (Test-Path $Params)) { New-Item -Path $Params -Force | Out-Null }
    New-ItemProperty -Path $Params -Name 'CrashOnCtrlScroll' -PropertyType DWord -Value 1 -Force | Out-Null
}

Write-Host ''
Write-Host 'Crash dump configuration applied. Reboot the guest.'
Get-ItemProperty -Path $CrashControl |
    Select-Object CrashDumpEnabled, AutoReboot, Overwrite, AlwaysKeepMemoryDump, DumpFile
