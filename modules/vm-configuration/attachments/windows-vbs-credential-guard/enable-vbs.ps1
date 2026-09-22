# Enables VBS, HVCI, and Credential Guard on Windows Server 2022.
# Run in an elevated PowerShell session inside the guest, then reboot.

$dg = 'HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard'
New-Item -Path $dg -Force | Out-Null
New-ItemProperty -Path $dg -Name EnableVirtualizationBasedSecurity -Value 1 -PropertyType DWord -Force | Out-Null

# 1 = Secure Boot only. Use 1 on KubeVirt VMs: they expose no IOMMU,
# so the value 3 (Secure Boot and DMA protection) keeps VBS from starting.
New-ItemProperty -Path $dg -Name RequirePlatformSecurityFeatures -Value 1 -PropertyType DWord -Force | Out-Null

$hvci = "$dg\Scenarios\HypervisorEnforcedCodeIntegrity"
New-Item -Path $hvci -Force | Out-Null
New-ItemProperty -Path $hvci -Name Enabled -Value 1 -PropertyType DWord -Force | Out-Null
New-ItemProperty -Path $hvci -Name Locked -Value 0 -PropertyType DWord -Force | Out-Null

# LsaCfgFlags: 0 = off, 1 = Credential Guard with UEFI lock, 2 = without UEFI lock.
$lsa = 'HKLM:\SYSTEM\CurrentControlSet\Control\Lsa'
New-ItemProperty -Path $lsa -Name LsaCfgFlags -Value 2 -PropertyType DWord -Force | Out-Null

bcdedit /set hypervisorlaunchtype auto

Write-Host 'VBS, HVCI, and Credential Guard configured. Reboot to apply.'
