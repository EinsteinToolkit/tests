# Abstract

This file contains instructions on how to create a Jenkins build slave using
VirtualBox running on an OSX host. The same instructions also work on a Linux
host.

# Setup

## Host preparation
* disable the application firewall
* edit /etc/pf.conf and add:
```
    block in on ! lo0 all
    pass out all
    # required for DHCP to work
    pass in proto udp from any to any port 68
    pass in inet proto icmp all icmp-type echoreq
    pass in inet6 proto ipv6-icmp all icmp6-type echoreq
    
    pass in proto tcp from any to any port 22
    pass in proto tcp from any to any port 20022
    pass in proto tcp from any to any port 20023
    pass in proto tcp from any to any port 20024
```
  where the last ones open up ports for use by the VMs
* load the file via `sudo pfctl -f /etc/pf.conf` and `pfctl -E` to enable the
  firewall
* enable clamshell mode via:
```
    sudo pmset -b sleep 0; sudo pmset -b disablesleep 1
    caffeinate -s
```
* disable the screen saver via the Screen Saver control panel
* disable the login screen saver via:
```
sudo defaults write /Library/Preferences/com.apple.screensaver loginWindowIdleTime 0
```
* disable password based logins in `/etc/ssh/sshd_config`. Note that we cannot just disable PAM b/c this breaks nohup (https://stackoverflow.com/questions/29112446/nohup-doesnt-work-with-os-x-yosmite-get-error-cant-detach-from-console-no-s):
```
    PasswordAuthentication no
    ChallengeResponseAuthentication no
    UsePAM yes
```
* disable spotligtht in the VMs, this requires system integrity protection to be disabled:
```
    sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.metadata.mds.plist
```
* alternatively, only disable indexing:
```
    sudo mdutil -a -i off
```
* install RDM or another resolution switch software if you want to be able to
  see the whole screen via vnc: https://github.com/avibrazil/RDM

## VM creation

* create a VirtualBox VM selecting "Mac OS X" as the type and (currently)
  "macOS 10.13 High Sierra (64-bit)" as the version
* disable audio support,
* disable any floppy
* provide 2048 MB of RAM
* provide 2 cores since there are only 2 physical cores on the host.
* provide 64 MB of graphics memory
* provide 50GB of disk space
* set up port forwarding, forwarding port 0.0.0.0:2000X to port 10.0.2.15:22
* make sure to add the port to `/etc/pf.conf` and restart the firewall
* follow these instructions to install the OS: https://www.howtogeek.com/289594/how-to-install-macos-sierra-in-virtualbox-on-windows-10/ (as of 2018-07-09) which shows how to creaate an installation ISO
  * Download the HighSierra installer from the App store on a real Mac
  * create ISO image, this must run on OSX
```
    hdiutil create -o /tmp/HighSierra.cdr -size 7316m -layout SPUD -fs HFS+J
    
    hdiutil attach /tmp/HighSierra.cdr.dmg -noverify -nobrowse -mountpoint /Volumes/install_build
    
    asr restore -source /Applications/Install\ macOS\ High\ Sierra.app/Contents/SharedSupport/BaseSystem.dmg -target /Volumes/install_build -noprompt -noverify -erase
    
    hdiutil detach /Volumes/OS\ X\ Base\ System

    hdiutil convert /tmp/HighSierra.cdr.dmg -format UDTO -o /tmp/HighSierra.iso

    mv /tmp/HighSierra.iso.cdr ~/Desktop/HighSierra.iso
```
  * hack VM, this must run on the intended host if the host is *not* a Mac
```
    VBoxManage modifyvm "High Sierra" --cpuidset 00000001 000306a9 04100800 7fbae3ff bfebfbff 
    
    VBoxManage setextradata "High Sierra" "VBoxInternal/Devices/efi/0/Config/DmiSystemProduct" "MacBookPro11,3"
    
    VBoxManage setextradata "High Sierra" "VBoxInternal/Devices/efi/0/Config/DmiSystemVersion" "1.0"
    
    VBoxManage setextradata "High Sierra" "VBoxInternal/Devices/efi/0/Config/DmiBoardProduct" "Mac-2BD1B31983FE1663"
    
    VBoxManage setextradata "High Sierra" "VBoxInternal/Devices/smc/0/Config/DeviceKey" "ourhardworkbythesewordsguardedpleasedontsteal(c)AppleComputerInc"
    
    VBoxManage setextradata "High Sierra" "VBoxInternal/Devices/smc/0/Config/GetKeyFromRealSMC" 1
```
  * run the installer (2 steps!). Insert the ISO image into the virtual CD
drive and boot up the VM, select a language and a timezone. Paritition the
disk using "Disk Utility" using "Mac OS Extended (Journaled)" which should be
the default. Then pick "Reinstall macOS" to start the installation process.
  * this will reboot and bring you back to the installation disk image.
  * power off the VM, remove the ISO image and restart the VM
  * in the boot prompt enter `cd "macOS Install Data"`, `cd "Locked Files"`,
    `cd "Boot Files"` and `finally boot.efi` to manually kick of the final
    stage of the installation process.

* once OSX is booted change the following:
  * enable remote login
  * enable screen share and set a password in the Advanced tab
  * disable sleep mode in the power preferences
  * set a plain blue background (for VNC) in the Desktop&Screensaver prefs
  * disable the screensaver
  * disable the login screen saver via:
```
sudo defaults write /Library/Preferences/com.apple.screensaver loginWindowIdleTime 0
```
  * enable automatic updates in the AppStore's preferences
  * I had to manually update the OS since a thunderbolt firmware update kept
    wanting to install itself
* disable password based logins in `/etc/ssh/sshd_config`. Note that we cannot just disable PAM b/c this breaks nohup (https://stackoverflow.com/questions/29112446/nohup-doesnt-work-with-os-x-yosmite-get-error-cant-detach-from-console-no-s):
```
    PasswordAuthentication no
    ChallengeResponseAuthentication no
    UsePAM yes
```
  * disable spotligtht in the VMs, this requires system integrity protection to be disabled:
```
    sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.metadata.mds.plist
```
  * alternatively, only disable indexing:
```
    sudo mdutil -a -i off
```

## OS updates

I case of glitches while updating the OS (happens to me). This is basically the
2nd step of the 2 step installation procedure.

This follows
https://raimue.blog/2017/06/09/upgrading-a-vm-from-macos-10-12-sierra-to-macos-10-13-high-sierra-in-virtualbox/
which lists these steps to do the update:


1. Boot the VM normally in VirtualBox.
1. Open “Install macOS 10.13 Beta.app”, click through until you get to “Restart”.
1. As soon as the screen turns black, start to hammer the F12 key. Make sure your keyboard is grabbed by the VM.
1. If you managed to hit F12 at the right time, the VirtualBox EFI should pop up. If the VM starts up normally, go back to step 2.
1. Now use your arrow keys to select Boot Manager and hit Return, then launch the EFI Internal Shell from there.
1. Inside the shell, type the following commands:
```
    Shell> fs1:
    FS1:\> cd "macOS Install Data"
    FS1:\macOS Install Data\> cd "Locked Files"
    FS1:\macOS Install Data\Locked Files\> cd "Boot Files"
    FS1:\macOS Install Data\Locked Files\Boot Files\> boot.efi
```
## disabling system integrity mode

Copied from http://anadoxin.org/blog/disabling-system-integrity-protection-from-guest-el-capitan-under-virtualbox-5.html .

One well known issue of running a guest MacOS X under VirtualBox is that it's not possible to enter Recovery OS by pressing the `Command+R` key combination on VM startup. In fact after reading some bug reports on VirtualBox bugtracker it seems that it's not possible to enter Recovery OS at all.

In order to access Installation environment under VirtualBox, you will need to enter the VirtualBox EFI BIOS by pressing F12 few times, at very early stage of guest VM boot up.

You will be greeted with an old school text mode BIOS interface, in which you should choose the `Boot Manager` option.

Inside, launch `EFI Internal Shell` to enter EFI commandline mode.

After getting the command prompt, switch to the `FS2:` drive:

```
2.0 Shell> FS2:
2.0 FS2:>
```

Of course, your drive number can be different, depending on the partition table structure you've chosen to have.

On the `FS2:` drive, in `com.apple.recovery.boot` directory, there is a EFI program inside the `boot.efi` file. We need to launch it.

```
2.0 FS2:\> cd com.apple.recovery.boot
2.0 FS2:\com.apple.recovery.boot\> boot.efi
```

When it will load, you need to launch the terminal, from which you will be able to use the `csrutil` command:

```
$ csrutil disable
```

### removing faulty prelinked kernel

From https://apple.stackexchange.com/questions/253906/mid-2010-macbook-pro-wont-boot-after-trying-to-install-macos-sierra

```
rm -f /Volumes/OSX/System/Library/PrelinkedKernels/prelinkedkernel
touch /Volumes/OSX/System/Library/Extensions
kextcache -u /Volumes/OSX
```

### ignoring a paorticular softare update

Following https://www.osx86.net/forums/topic/22384-how-to-turn-off-update-in-appstore-this-message-thunderbolt-firmware-update-12/

```
softwareupdate -l # to list which ones are available
sudo softwareupdate --ignore ThunderboltFirmwareUpdate1.2
```

where one apparently has to leave out the version information that is displayed
by `-l` after a hyphen.

### installing updates from command line

Eg https://www.macrumors.com/how-to/update-macos-terminal-command/ basically the same as ignoring them

```
sudo softwareupdate --restart --install 'macOS High Sierra 10.13.3 Supplemental Update- '
```

which apparently should include everyting on first line of output of the `-l` command incl. the *hidden* whitespace...
