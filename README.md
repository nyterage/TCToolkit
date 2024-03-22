# TCToolkit
A Toolkit for World of Warcraft Theorycrafting, focused on data generation

# Stat Sims
Generates graphs on stat scaling, focused mostly on DPS/point scaling. Proper use of this data generation can give you information on secondary balance. Any other use of that data may be misleading!
# How to Use
Built using Python 3.10.11, may not run on older versions!

Download the SimC nightly zip from [here](http://downloads.simulationcraft.org/nightly/?C=M;O=D)

Place the extracted files in the simc directory

OR build SimC from source if you know what youre doing, codebase can be found [here](https://github.com/simulationcraft/simc)

Open a terminal in the main directory and run `pip install -r requirements.txt`

Adjust any options you want to change in dir/stat_sim/stat_sim.py

Run stat_sim.py and wait. Depending on your settings, this can take many hours, or even days to complete and generate the chart data!

# Recommendations
Would highly recommend installing [vscode](https://code.visualstudio.com/) with the pylance, python and pythondebugger extensions so you can easily edit the configuration and run with one click.