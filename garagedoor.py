from gpiozero import LED
from gpiozero import Buzzer
from gpiozero import Button
from signal import pause
import time
from time import sleep
import smtplib
import _thread
from signal import pause

# this file contains the email credentials
import emailcred


#Initializing
print('Initializing the system ...')


# Initalizing LED Objects
greenLED = LED(17)
redLED = LED(23)

# Initalizing Green LED ON
greenLED.on();
print('Garage Closed')

# Initalizing Button Object and connect it to GPIO16
button = Button(16)

# create a variable "button" and connect it to GPIO26
buzzer = Buzzer(26)

# For Tracking Garage Door State
closed = False
open = True
garageState = closed;

#Setting up connection to SMTP Server for sending email/sms.
print('Preparing SMTP connection ...')
#Function to call on new thread
#Because of race conditions, this needs to be done quickly or on a different thread
def send_msg():
    # we will use Gmail accounts and SMTP protocol
    server = smtplib.SMTP_SSL( 'smtp.gmail.com', 465)

    # get login credentials from the file "emailcred.py"
    server.login( emailcred.FROM, emailcred.PASS )
    #Compile message string to print and send.
    #Ex: 'Button was pressed at 5:50:20 PM'
    actionMessage = ''.join([ '\n Garage was opened at ',
                        time.strftime('%I:%M:%S %p')])
    print(actionMessage)
    server.sendmail(emailcred.FROM, emailcred.TO, actionMessage)
    server.quit()

def thread_send_msg():
    _thread.start_new_thread(send_msg, ())

def beepBuzzer():
# the following beep function turns the buzzer on for 0.5 second,
# and turn it off for 0.5 second. It repeats 15 times.
    for i in range(0, 15):
        buzzer.beep(0.5, 0.5)


def openGarage():
    global garageState
    greenLED.off()
    redLED.on()
    print('Opening Garage...')
    send_msg()
    beepBuzzer()
    print('Opened!')
    garageState = open

def closeGarage():
    global garageState
    redLED.off()
    greenLED.on()
    print('Closing garage...')
    beepBuzzer()
    print('Closed!')
    garageState = closed

#Running actual program

# when the button pressed, send_msg() is called
    
def toggleGarage():
    global garageState
    if garageState == closed:
        openGarage()
    else:
        closeGarage()

# Set the button press handler to toggleGarage
button.when_pressed = toggleGarage

#Using threads
#button.when_pressed = thread_send_msg


# The pause function forces the program to wait and not exit
# To exit from terminal, use ^ctrl+c
pause()
