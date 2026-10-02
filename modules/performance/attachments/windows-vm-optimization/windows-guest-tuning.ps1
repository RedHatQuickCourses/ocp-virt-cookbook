#Requires -RunAsAdministrator
<#
    Windows guest tuning for OpenShift Virtualization.
    Tested on Windows Server 2022 and Windows 11 23H2.

    Run from an elevated PowerShell prompt inside the guest:
        Set-ExecutionPolicy -Scope Process Bypass -Force
        .\windows-guest-tuning.ps1

    Reboot afterwards so the power plan and registry changes take effect.
#>

$ErrorActionPreference = 'Continue'

Write-Host '== Power plan =='
# High performance scheme GUID is fixed across Windows releases.
$HighPerformance = '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'
powercfg /setactive $HighPerformance
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 0
powercfg /change disk-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /hibernate off

Write-Host '== Hardware clock is UTC =='
# Matches spec.domain.clock.utc on the VirtualMachine.
New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\TimeZoneInformation' `
    -Name 'RealTimeIsUniversal' -PropertyType DWord -Value 1 -Force | Out-Null

Write-Host '== Disable SysMain (Superfetch) =='
Stop-Service -Name 'SysMain' -Force -ErrorAction SilentlyContinue
Set-Service -Name 'SysMain' -StartupType Disabled -ErrorAction SilentlyContinue

Write-Host '== Disable scheduled defragmentation =='
Disable-ScheduledTask -TaskPath '\Microsoft\Windows\Defrag\' -TaskName 'ScheduledDefrag' `
    -ErrorAction SilentlyContinue | Out-Null

Write-Host '== Keep TRIM/UNMAP enabled =='
fsutil behavior set DisableDeleteNotify 0

Write-Host '== Processor scheduling favors background services =='
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' `
    -Name 'Win32PrioritySeparation' -Value 24

Write-Host '== Visual effects set to best performance =='
$VisualFx = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects'
if (-not (Test-Path $VisualFx)) { New-Item -Path $VisualFx -Force | Out-Null }
New-ItemProperty -Path $VisualFx -Name 'VisualFXSetting' -PropertyType DWord -Value 2 -Force | Out-Null

Write-Host '== VirtIO network adapter tuning =='
$VirtioNics = Get-NetAdapter | Where-Object { $_.InterfaceDescription -like '*VirtIO*' }
foreach ($Nic in $VirtioNics) {
    Write-Host ("   adapter: {0}" -f $Nic.Name)
    # Receive Side Scaling pairs with networkInterfaceMultiqueue on the VM spec.
    Set-NetAdapterAdvancedProperty -Name $Nic.Name -RegistryKeyword '*RSS' `
        -RegistryValue 1 -NoRestart -ErrorAction SilentlyContinue
    # Do not let Windows power down the virtual NIC.
    Set-NetAdapterPowerManagement -Name $Nic.Name -AllowComputerToSleep Disabled `
        -ErrorAction SilentlyContinue
}
if ($VirtioNics) { Restart-NetAdapter -Name $VirtioNics.Name -ErrorAction SilentlyContinue }

Write-Host ''
Write-Host 'Tuning applied. Reboot the guest to activate all settings.'
