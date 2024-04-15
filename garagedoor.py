from gpiozero import LED
from gpiozero import Buzzer
from gpiozero import Button
from signal import pause
import time
from time import sleep
import smtplib
import _thread
from signal import pause
import random
import os

# this file contains the email credentials
import emailcred


#Initializing
print('Initializing the system ...')


# Initalizing LED Objects
greenLED = LED(17)
redLED = LED(27)

# Initalizing Green LED ON
greenLED.on();
print('Garage Closed')

# Initalizing Button Object and connect it to GPIO16
button = Button(16)

# create a variable "buzzer" and connect it to GPIO26
buzzer = Buzzer(26)

# For Tracking Garage Door State
closed = False
Open = True
garageState = closed;

#Setting up connection to SMTP Server for sending email/sms.
print('Preparing SMTP connection ...')
#Function to call on new thread
#Because of race conditions, this needs to be done quickly or on a different thread
def send_msg(message):
    # we will use Gmail accounts and SMTP protocol
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

    # get login credentials from the file "emailcred.py"
    server.login(emailcred.FROM, emailcred.PASS)

    # Compile message string to print and send.
    if message == 'open':
        # Ex: 'Button was pressed at 5:50:20 PM'
        actionMessage = ''.join(['\n Garage was opened at ',
                            time.strftime('%I:%M:%S %p')])
        print(actionMessage)
        server.sendmail(emailcred.FROM, emailcred.TO, actionMessage)
        server.quit()
    if message == 'code':
        random_number = random.randint(10000, 99999)
        # Delete the file if it exists and then write the new random number to it
        if os.path.exists('code.txt'):
            os.remove('code.txt')
        # Correctly open the file with write and create flags
        file_descriptor = os.open('code.txt', os.O_WRONLY | os.O_CREAT)
        with os.fdopen(file_descriptor, 'w') as file:
            file.write(str(random_number))

        server.sendmail(emailcred.FROM, emailcred.TO, str(random_number))

    if message == 'fail':
        actionMessage = ''.join(['\n A user attempted to open your garage at ',
                            time.strftime('%I:%M:%S %p')])
        server.sendmail(emailcred.FROM, emailcred.TO, actionMessage)

def thread_send_msg():
    _thread.start_new_thread(send_msg, ())

def beepBuzzer():
# the following beep function turns the buzzer on for 0.5 second,
# and turn it off for 0.5 second. It repeats 15 times.
    for i in range(0, 15):
        buzzer.beep(0.5, 0.5)

def authenticate(type):
    if type == 'password':
        while True:
            print('Enter password or swipe card')
            password = input('Password: ')
            with open('passwd.txt', 'r') as f:
                for line in f:
                    if line.strip() == password:
                        print('Password authenticated')
                        print('Sending 2FA SMS code...')
                        send_msg('code')
                        return True
                # If the loop completes without finding a match, return False
            print('Authentication Failure')
            return False
    if type == 'code':
        attempts = 0
        while attempts < 3:
            print('Enter 5-digit Code')
            password = input('Code: ')
            with open('code.txt', 'r') as f:
                for line in f:
                    if line.strip() == password:
                        print('User authenticated')
                        return True
                    else:
                        print('SMS code invalid.')
                        attempts += 1
        print('Maximum input attempts reached. Garage remains closed.')
        return False
    
def openGarage():
    global garageState

    success = authenticate('password')
    if not success:
        return

    success = authenticate('code')

    if not success:
        print('Failed to authenticate. Please try again.')
        send_msg('fail')
        return

    greenLED.off()
    redLED.on()
    print('Opening Garage...')
    send_msg('open')
    beepBuzzer()
    print('Opened!')
    garageState = Open

def closeGarage():
    global garageState
    redLED.off()
    greenLED.on()
    print('Closing garage...')
    beepBuzzer()
    print('Closed!')
    garageState = closed

def printGarageState():
    global garageState
    if garageState == closed:
        print('The garage is closed')
    else:
        print('The garage is open')

def toggleGarage():
    global garageState
    if garageState == closed:
        openGarage()
    else:
        closeGarage()
    printGarageState()

# Set the button press handler to toggleGarage

button.when_pressed = toggleGarage

# The pause function forces the program to wait and not exit
# To exit from terminal, use ^ctrl+c
pause()
