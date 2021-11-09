Music Bracelet
by Lisa Zhu

Built on pocketbeagle with python, this bracelet can provide combined effects of vibration and LED while playing music.
Please visit for a complete tutorial and build instructions.

Libraries to install:
-speaker:
	sudo apt-get update 
	sudo apt-get install alsa-utils libasound2 -y
	sudo apt-get install mplayer -y
-SPI screen:
	sudo apt get update
	sudo pip3 install upgrade Pillow
	sudo pip3 install adafruit circuitpython busdevice
	sudo pip3 install adafruit circuitpython rgb display
	sudo apt get install ttf dejavu y
-LED Strip:
	download the files in the LED_Strip folder

Implementation Files:
In Project_1/LED_Strip, do ./run, this will connect the opc server of the LED strip;
Open another terminal, in Project_2/SPI_screen, do ./run, this will start the program.

To autoboot the system, use sudo crontab -e, and add two lines:
@reboot sleep 30 && sh /var/lib/cloud9/ENGI301/Project_1/LED_Strip/run > /var/lib/cloud9/ENGI301/Project_1/LED/log/cronlog 2>&1
@reboot sleep 30 && sh /var/lib/cloud9/ENGI301/Project_1/SPI_screen/run > /var/lib/cloud9/ENGI301/Project_1/SPI_screen/log/cronlog 2>&1

Instructions for use:
1. Clone the repository in /var/lib/cloud9 of PocketBeagle
2. Assemble the system according to the hackster page
3. Run the system using two run files
4. Enjoy the bracelet! 