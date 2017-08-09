# lightning
Raspberry Pi/MOD-1016 lightning sensor python source.  The original code relied on output to the monitor; I modified it to log data to a file and remove most, if not all, of the print statements.  The original idea came from https://coffeewithrobots.com/detecting-lightning-with-a-raspberry-pi/, which has a repo at https://github.com/pcfens/RaspberryPi-AS3935

I added the ability to tweet lightning info by modifying code from Hexalyse repo at https://github.com/Hexalyse

Note that strikes that occur at the end of a storm will not be tweeted. For instance, if the code accumulates one or more strike after a tweet and no further strikes occur, those old strikes will not be tweeted.  Hexalyse solved this by calling the interrupt routine inside the main loop, in their case, every 10 seconds.  This didn't work for me; when I polled the sensor, it routinely report strikes when none were present.  

This code uses the Python logger to save the strike data in a .csv file.  I use the WARNING level to avoid clutter from other debugging.  You can import that data to a spreadsheet program and do plots 

Since it can run without a monitor, I added an indicator LED, so I can tell if it is running.  
