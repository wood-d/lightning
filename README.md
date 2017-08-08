# lightning
Raspberry Pi/MOD-1016 lightning sensor python source.  This runs as a headless app logging data to a .csv file while tweeting summary data.  The twitter part came from https://github.com/Hexalyse, the MOD-1016 part came from https://coffeewithrobots.com/detecting-lightning-with-a-raspberry-pi/

Note that strikes that occur at the end of a storm will not be tweeted. For instance, if the code accumulated one or more strike after a tweet and no further strikes occur for 1 day, those old strikes will not be tweeted.

This code used the Python logger to save the strike data in a .csv file.  I use the WARNING level to avoid clutter from other debugging.  
