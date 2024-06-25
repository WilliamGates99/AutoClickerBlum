# Blum Auto Clicker
Blum Auto Clicker is an improved auto-clicker script that automates collecting stars in the Telegram game, Blum. The script supports randomizing star collection and automatic launch of games until tickets run out.

# How to Use AutoClikerBlum Script

### • Step 1: Download and Install Python
Download and install the latest version of Python from [python.org](https://www.python.org/). 
Make sure to check the <code>Add Python to PATH</code> option during the installation process.

### • Step 2: Verify Python and pip installation
Open a command prompt and enter the following commands to verify the installation of Python and pip:
```sh
python --version
pip --version
```

### • Step 3: Download Blum Auto Clicker from GitHub
Click on the <code style="color : green">Code</code> button, and then click on <code>Download Zip</code> to download the source code.

### • Step 4: Install the Required Dependencies
On the command-line, navigate to the script directory and install the required dependencies:
```sh
cd "path\to\AutoClickerBlum"
pip install -r requirements.txt
```
Alternatively, to launch the command-line directly in the desired directory, you can:<br>
• Enter <code>cmd</code> in the directory's address bar.<br>
• Or <code>right-click</code> in the directory and select <code>Open in Terminal</code>.

### • Step 5: Launch the Blum Bot on Telegram Desktop or Telegram Web.
The script supports both versions.

### • Step 6: Run the script
Click on <code>main.py</code> or run the script from command-line:
```sh
python main.py
```
### • Step 7: Select the Window that is Running the Blum Bot
Enter the suggested window number.<br>
• If you are running Blum on Telegram desktop, enter the number in front of the <code>TelegramDesktop</code>.<br>
• If you are running Blum on Telegram web, enter the number in front of the <code>Blum - Browser Name</code>.

### • Step 8: Randomize Star Clicking
Enter a value between 0 and 1 to randomize star clicking, where 1 means collecting all the stars. (The choice of value depends on many factors: screen size, window size, etc.)<br>
• If you enter <code>1</code>, the script will collect around 200-250 stars. <b>But it will increase the risk of automated bot detection and banning of your Blum account</b>.<br>
• I recommend choosing a value between <code>0.04</code> and <code>0.08</code> to collect around 100-160 stars.

### • Step 9: Start the Script
Press F6 to start/pause the script.

# Additional Recommendations:
Reduce the size of the game window so that there is less margin around it.<br>
The script can sometimes click past the game window and a window with information about closing the game will appear.
