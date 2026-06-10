# HABMOT-I


## Glossary
- Target -> The NVIDIA computer on which the camera are pluged into (it is a small square box). 
- Host -> The computer on which the Target is connected when flashing  
- Flash -> Pressing the central button + reset. Allows using the Target as a USB key to update it from *NVIDIA SDK manager* on the Host. 

## Resources
The main resources should be from the *stereolabs* in priority (and probably solely): 
https://www.stereolabs.com/docs

WARNING: Using documentation from nvidia official website (or other official resources) will probably results in the Target being in a failing state. In case of emergency (e.g. Target won't turn on anymore), flashing Target (see [Initialization of Target](#initialization-of-target) below) should work. 


## Initialization of Target

### Prerequisites
The Host cannot be just any computer. We are limited to what is mentioned on the page <https://developer.nvidia.com/sdk-manager> in the section **Base SDKs Host Operating System Compatibility Matrix**. Also, the computer must be native on the mentioned operating system. The choice of JetPack depends on the SDKs we want to use (DeepStream, Holoscan, etc.). That said, using the docker version of the SDK manager seems to solve most of the compatibility issues (that is navigating the different versions of Ubuntu so any SDK version can be used).


### Troubleshooting

#### DPKG failed**
If you get the error "the DPKG command fails" (spoiler, it will fail...), you need to install (on the Host) a compatibility layer (assuming the Host is under Linux):
```bash
sudo apt install qemu-user-static binfmt-support  
sudo update-binfmts --enable  
```


### USB in the docker
Contrary to what the documentation mentions, you need to actively pass the USB to the docker. The command to launch the docker should therefore be the following (note that this command assumes that the Host is under Linux):
```bash
docker run -it --rm --privileged -v /dev/bus/<usb:/dev/bus/usb> -v /<dev:/dev> --network host sdkmanager --cli
```


### Non-optimal USB
If you get the mention that the USB is not optimal, there are potentially several causes.
- Using a virtualbox (not confirmed, as I had the same problem with Docker, solved by the next method)
- Bad USB port generation (confirmed). Solution: a USB-C to USB-C cable guarantees that the ports are compliant.


## Installing/updating Target drivers
As stated before, the main 

1. ZED SDK should first be installed
2. ZED Tools should then be installed
3. Create a link to the ZED Tools folder


