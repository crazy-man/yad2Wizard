# yad2Wizard v0.0.4

yad2Wizard is an open source application for popping up ads on popular Israeli website yad2 for free.

Currently application consists of:
 * pop_up.py - command line standalone that performs pop up of ads
 * yad2Wizard.pyw - GUI window written using PyQT5, which also handles scheduling.

Currently it is only tested on Windows 10.

Installation:

Prerequisites:
 * [Python >= 3.4.x](https://www.python.org/downloads/) - make sure to include pip
 * selenium framework with python bindings (pip install selenium)
 * [Google Chrome browser](https://www.google.com/chrome/browser/desktop/index.html)
 * chromedriver(download executable from [here](http://chromedriver.storage.googleapis.com/2.24/chromedriver_win32.zip) and drop somewhere in your PATH)
 * [PyQT5](https://sourceforge.net/projects/pyqt/files/latest/download)

Usage:
 * run in cmd: python yad2Wizard.py (make sure "python" is in your PATH and python version is 3.x)
 * In the main window enter your credentials and click "Save" button. 
 
	(Optionally test your credentials using "Test Credentials" button)
 * Click "Pop Up Now!" button. 
 * In the status bar you will see status and the next time of running.
 * Do NOT close the window and cmd terminal, otherwise it will not continue to wake up.
 * Enjoy!
	
Known Issues:

 * No silent mode
 * No service mode
 * No start on start up
 * No multiple users support
 * Error handling is very poor

License:

Use at your own risk. Author is not responsible for blocked IPs, accounts and other things that might happen to you.
