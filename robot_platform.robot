# Take initial snapshot of the operational state of the device
# and save the output to a file

*** Settings ***
# Importing test libraries, resource files and variable files.
Library        genie.libs.robot.GenieRobot
Library        pyats.robot.pyATSRobot
Library        unicon.robot.UniconRobot

*** Variables ***
# Define the pyATS testbed file to use for this run
${testbed}     testbed/routers.yml 

*** Test Cases ***
# Creating test cases from available keywords.

Connect
    # Initializes the pyATS/Genie Testbed
    use genie testbed "${testbed}"

    # Connect to both device
    connect to device "R1"
    connect to device "R2"

Profile the devices
    Profile the system for "platform" on devices "R1;R2" as "./platform"
 