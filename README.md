# plotbot

Raspberry Pi code that drives stepper motors and sensors on an old 3D printer allowing for 2D images to be drawn on the base plate with a pen.

Demo Video: https://www.youtube.com/watch?v=gwPj64Iiqy4

#plotbot.py
This is a command line interface program that allows for precise movement of the print head along a single axis.  Each 
movement will report the current position of the print head and save this to a configuration file `~/.plotbot.json`
See [plotbot.json](plotbot.json) in this repo for example

This script is useful for calibrating and saving known positions 
whenever the physical setup is changed. e.g. if a different print surface or writing implement is used. e.g. paper vs 
white board, or ballpoint pen vs crayon.  After defining configuration values for the current physical setup, the json 
file can be saved as a "profile" for later reuse of that physical configuration in special purpose applications.

##Usage
`$ ./plotbot.py -h` - Will display usage information. 
 
##Calibration
 If print heads have been moved while powered down or a program fails in anyway, it is recommended to run the `reset` 
   command.  This return the print-head to its home position and will reset any saved (and probably incorrect) 
   information about the current position. 

##Movement
###Move
The move command will move the print head.  Use Adding + or - to will move to a relative position. 
    - 5 steps = 1 mm for x and y axis
    - 156.25 steps = 1 mm for z axis
    
#### Move Command Examples:
 - `./plotbot.py move_ x 50 mm` will move the print head _either_ to the left _or_ the right so that it is 5 cm 
from the min(0) position.
 - `./plotbot.py move z +50 steps` will move the print head down 50 steps from the current position 

###Goto
The goto command will move the print head to named positions saved in the active profile. Built-in positions include 
`min`,`mid`, and `max`.
Example
   
##Profiles
Configuration profiles are maintained in the user's `~/.plotbot.json`.  Profiles can be modified with the `set` and 
`profile` commands. 
###Profile Command Examples :
   - `status` Display the active profile 
   - `set y top-of-page`  Saves the current y axis position as "top-of-page"  
   - `profile --list`  Display available profiles from the users config file
   - `profile --load="dry-erase-board"`  Set the active profile to "dry-erase-board" 
   - `profile --save="ballpoint-on-paper"` Saves the current active profile as a new profile called 
     "ballpoint-on-paper"
   - `profile --delete="experment-1"` Deletes the "experiment-1" profile
   