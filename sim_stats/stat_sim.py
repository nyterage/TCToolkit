#!/usr/bin/env python3
import subprocess
import pandas as pd
import plotly.graph_objects as go
import os
import sys
import platform
from inputimeout import inputimeout, TimeoutOccurred

# Input Variables
input_profile = "unh_tst.simc" # This should be a bare profile, only character info and gear
sim_class = "death_knight"
specilization = "unholy"
fight_style = "Patchwerk" # Patchwerk, and DungeonSlice are the likely most useful for this
desired_targets = 1 # Number of enemy targets to sim, DungeonSlice ignores this
sim_duration = 300 # Duration of the sim in seconds
tar_err = 0.05 # Sims target Error
iter = 15000 # Max number of Iterations to run, will stop at this number if target error has not been reached
pos = 1 # Plot only positive values from the current rating, set to 0 to generate both positive and negative values
plot_step = 10 # Difference in Rating between each plot point
plot_points = 1000 # Number of plot points to generate
rolling_avg = 18 # Rolling average for DPS per point, set to 1 to disable rolling average
report_details = 1
optimal_raid = 1

#----------------------------------------------------------------------------------------------------------------------------------------------------#
# Matrix Sims attempt to highlight interactions between stats, showing how the value of one stat will change based on the rating of another          #
# To enable matrix sims, set the variable for the stat you want to scale up to True, this will then generate the dps/point value for all other stats #
# Warning, matrix sims can take an extremely long time to run, especially if you have multiple stats enabled                                         #
#----------------------------------------------------------------------------------------------------------------------------------------------------#
matrix_step = 300 # Difference in Rating between each matrix point, applies to the main matrix stat (option below)
matrix_points = 34 # Number of points to generate in the matrix, applies to the main matrix stat (option below)
matrix_secondary_step = 100 # Difference in Rating between each matrix point, applies to the secondary matrix stats
matrix_secondary_points = 5 # Number of data points to generate in the matrix, applies to the secondary matrix stats. Will be averaged, higher numbers will increase accuracy but also increase compute time
matrix_iter = 15000 # Max number of Iterations to run for the matrix sims, will stop at this number if target error has not been reached

# Profile Modifications
modify_base_profile = True # Set to False if you dont want to modify the base profile with any of the values below
# Set to 1 to enable that tier set bonus, set to 0 to disable it
tier_set_bonus_2pc = 1
tier_set_bonus_4pc = 1
tier_set_number = 31 # Set the tier set number, the current tier at the time of writing is Amirdrassil, which is tier_set_number = 31
# If you want to remove the influence of these things on the sim, make sure they are set to "disabled"!
# Otherwise, syntax is the name in snake_case followed by the rank of the item, e.g. potion = "elemental_potion_of_ultimate_power_3"
# if the item has no rank, omit the number, e.g. food = "sizzling_seafood_medley"
potion = "disabled"
food = "disabled"
flask = "disabled"
augmentation = "disabled"
temporary_enchants = "disabled"
# Make sure you set this to true if you want to eliminate the influence of trinkets on the data!
disable_trinekts = True
disable_weapon_effects = True
use_2h = True # Only applies to Warrior and FDK, where might of the frozen wastes and single minded fury may be a factor
# Disable Gear Effects (Excludes weapons, trinkets and Tier set (set above))
disable_gear_effects = True

# Base Stat Modifications
modify_current_stats = True
# Set the base rating from gear for each stat, would highly recommend setting to 0 and setting pos to 1 unless you know what you're doing
base_haste_rating = 0 # Set to 0 to set haste in the input ptofile to 0, otherwise set whatever value you wish
base_crit_rating = 0 # Set to 0 to set crit in the input ptofile to 0, otherwise set whatever value you wish
base_mastery_rating = 0 # Set to 0 to set mastery in the input ptofile to 0, otherwise set whatever value you wish
base_versatility_rating = 0 # Set to 0 to set versatility in the input ptofile to 0, otherwise set whatever value you wish
base_primary_rating = 0 # Set to 0 to set primary stat in the input ptofile to 0, otherwise set whatever value you wish

# Stat Sim Variables
sim_haste = True
sim_crit = True
sim_mastery = True
sim_vers = True
sim_primary = True
generate_stat_charts = True
# These Only Apply to basic stat sims, not matrix sims
graph_haste = True
graph_crit = True
graph_mastery = True
graph_vers = True
graph_primary = True

# Matrix Sim Variables
# Enabling any of these will disable the normal stat scaling sims! compute time would be far too long.
sim_haste_matrix = False
sim_crit_matrix = False
sim_mastery_matrix = False
sim_vers_matrix = False
sim_primary_matrix = False
generate_matrix_charts = False
# Enables or Disables the generation of these stats as "secondary" stats in the matrix.
# e.g. disabling all but haste would generate charts for all enabled primary stats (options above), with as the haste secondary.
# allows for mixing and matching for deeper exploration. 
# Will also enable or disable them in chart generation, no matter if the sim is run or youre just generating charts.
gen_haste_secondary_matrix = True
gen_crit_secondary_matrix = True
gen_mastery_secondary_matrix = True
gen_vers_secondary_matrix = True
gen_primary_secondary_matrix = True

# Graph Variables
graph_width = 2000 # Width of the graph in pixels
graph_height = 1000 # Height of the graph in pixels
graph_open = True # Open the interactive graph in a browser window when the script finishes, will still save the image to the output directory if set to false
# Style of the graph, useful variations are "lines+markers", "lines", "markers"
graph_style = "lines+markers"
# Only One of these two should be enabled at any one point in time!
graph_dps_per_point = True # Probably the only useful graph
graph_dps = False # Plots DPS vs Rating, same thing youd get in the simc html output, but bigger!

#----------------------------------------------------------------------------------------#
# Code Starts Here, dont touch anything below this line unless you know what youre doing #
#----------------------------------------------------------------------------------------#
# Directories
profile_dir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "profiles")
simc_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'simc')))
data_dir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "raw_data")
output_dir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "data_output")
chart_output_dir = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "chart_output")
weapon = ""

# Find the primary stat of the profile
def switch_primary():
    match sim_class:
        case "death_knight":
            match specilization:
                case "blood":
                    return "strength"
                case "frost":
                    return "strength"
                case "unholy":
                    return "strength"
        case "demon_hunter":
            match specilization:
                case "havoc":
                    return "agility"
                case "vengeance":
                    return "agility"
        case "druid":
            match specilization:
                case "balance":
                    return "intellect"
                case "feral":
                    return "agility"
                case "guardian":
                    return "agility"
                case "restoration":
                    return "intellect"
        case "evoker":
            match specilization:
                case "augmentation":
                    return "intellect"
                case "devastation":
                    return "intellect"
                case "preservation":
                    return "intellect"
        case "hunter":
            match specilization:
                case "beast_mastery":
                    return "agility"
                case "marksmanship":
                    return "agility"
                case "survival":
                    return "agility"
        case "mage":
            match specilization:
                case "arcane":
                    return "intellect"
                case "fire":
                    return "intellect"
                case "frost":
                    return "intellect"
        case "monk":
            match specilization:
                case "brewmaster":
                    return "agility"
                case "mistweaver":
                    return "intellect"
                case "windwalker":
                    return "agility"
        case "paladin":
            match specilization:
                case "holy":
                    return "intellect"
                case "protection":
                    return "strength"
                case "retribution":
                    return "strength"
        case "priest":
            match specilization:
                case "discipline":
                    return "intellect"
                case "holy":
                    return "intellect"
                case "shadow":
                    return "intellect"
        case "rogue":
            match specilization:
                case "assassination":
                    return "agility"
                case "outlaw":
                    return "agility"
                case "subtlety":
                    return "agility"
        case "shaman":
            match specilization:
                case "elemental":
                    return "intellect"
                case "enhancement":
                    return "agility"
                case "restoration":
                    return "intellect"
        case "warlock":
            match specilization:
                case "affliction":
                    return "intellect"
                case "demonology":
                    return "intellect"
                case "destruction":
                    return "intellect"
        case "warrior":
            match specilization:
                case "arms":
                    return "strength"
                case "fury":
                    return "strength"
                case "protection":
                    return "strength"
                
def switch_weapon():
    match sim_class:
        case "death_knight":
            match specilization:
                case "blood":
                    return "trainees_sword,id=73210"
                case "frost":
                    if( use_2h ):
                        return "trainees_sword,id=73210"
                    else:
                        return "worn_axe,id=37\n off_hand=worn_axe,id=37"
                case "unholy":
                    return "trainees_sword,id=73210"
        case "demon_hunter":
            return "worn_axe,id=37\n off_hand=worn_axe,id=37"
        case "druid":
            return "farmers_broom,id=114980"
        case "evoker":
            return "farmers_broom,id=114980"
        case "hunter":
            match specilization:
                case "beast_mastery":
                    return "worn_shortbow,id=2504"
                case "marksmanship":
                    return "worn_shortbow,id=2504"
                case "survival":
                    return "farmers_broom,id=114980"
        case "mage":
            return "farmers_broom,id=114980"
        case "monk":
            return "farmers_broom,id=114980"
        case "paladin":
            match specilization:
                case "holy":
                    return "farmers_broom,id=114980"
                case "protection":
                    return "worn_axe,id=37"
                case "retribution":
                    return "trainees_sword,id=73210"
        case "priest":
            return "farmers_broom,id=114980"
        case "rogue":
            match specilization:
                case "assassination":
                    return "sharp_dirk,id=50057\n off_hand=sharp_dirk,id=50057"
                case "outlaw":
                    return "worn_shortsword,id=25\n off_hand=sharp_dirk,id=50057"
                case "subtlety":
                    return "sharp_dirk,id=50057\n off_hand=sharp_dirk,id=50057"
        case "shaman":
            return "farmers_broom,id=114980"
        case "warlock":
            return "farmers_broom,id=114980"
        case "warrior":
            match specilization:
                case "arms":
                    return "trainees_sword,id=73210"
                case "fury":
                    if( use_2h ):
                        return "trainees_sword,id=73210\n off_hand=trainees_sword,id=73210"
                    else:
                        return "worn_axe,id=37\n off_hand=worn_axe,id=37"
                case "protection":
                    return "worn_axe,id=37"

# Lists of elements to add to the simc profile
sim_mod = []
profile_mod = []

base_profile = open(os.path.join(profile_dir, input_profile), "r")

is_matrix_sim = False
if any( x == True for x in [sim_haste_matrix, sim_crit_matrix, sim_mastery_matrix, sim_vers_matrix, sim_primary_matrix] ):
    is_matrix_sim = True

if( is_matrix_sim == False ):
    sim_mod.append("dps_plot_iterations="+str(iter)+"\n")
    sim_mod.append("dps_plot_points="+str(plot_points)+"\n")
    sim_mod.append("dps_plot_step="+str(plot_step)+"\n")
if( is_matrix_sim == True ):
    sim_mod.append("dps_plot_iterations="+str(matrix_iter)+"\n")
    sim_mod.append("dps_plot_points="+str(matrix_secondary_points)+"\n")
    sim_mod.append("dps_plot_step="+str(matrix_secondary_step)+"\n")
sim_mod.append("target_error="+str(tar_err)+"\n")
sim_mod.append("fight_style="+fight_style+"\n")
sim_mod.append("desired_targets="+str(desired_targets)+"\n")
sim_mod.append("max_time="+str(sim_duration)+"\n")
sim_mod.append("report_details="+str(report_details)+"\n")
sim_mod.append("optimal_raid="+str(optimal_raid)+"\n")
sim_mod.append("dps_plot_positive="+str(pos)+"\n")
sim_mod.append("iterations="+str(iter)+"\n")
sim_mod.append("html=" + os.path.join(output_dir, "output.html") + "\n")
sim_mod.append("json2=" + os.path.join(output_dir, "output.json") + "\n")

with open(os.path.join(profile_dir, f"{sim_class}_{specilization}_input.simc"), "w+") as sim_profile:
    for i in sim_mod:
        sim_profile.write(i)
    sim_profile.write("\n")
    sim_profile.write(base_profile.read())
    base_profile.close()
    if( modify_current_stats ):
        profile_mod.append("gear_crit_rating="+str(base_crit_rating)+"\n")
        profile_mod.append("gear_haste_rating="+str(base_haste_rating)+"\n")
        profile_mod.append("gear_mastery_rating="+str(base_mastery_rating)+"\n")
        profile_mod.append("gear_versatility_rating="+str(base_versatility_rating)+"\n")
        if( sim_primary ):
            profile_mod.append("gear_"+switch_primary()+"="+str(base_primary_rating)+"\n")
    if( modify_base_profile ):
        profile_mod.append("potion="+potion+"\n")
        profile_mod.append("food="+food+"\n")
        profile_mod.append("flask="+flask+"\n")
        profile_mod.append("augmentation="+augmentation+"\n")
        profile_mod.append("temporary_enchant="+temporary_enchants+"\n")
        profile_mod.append("set_bonus=tier"+str(tier_set_number)+"_2pc="+str(tier_set_bonus_2pc)+"\n")
        profile_mod.append("set_bonus=tier"+str(tier_set_number)+"_4pc="+str(tier_set_bonus_4pc)+"\n")
        if( disable_trinekts ):
            profile_mod.append( "trinket1=\n" )
            profile_mod.append( "trinket2=\n" )
        if( disable_gear_effects ):
            profile_mod.append("head=\n")
            profile_mod.append("neck=\n")
            profile_mod.append("shoulder=\n")
            profile_mod.append("back=\n")
            profile_mod.append("chest=\n")
            profile_mod.append("wrist=\n")
            profile_mod.append("hands=\n")
            profile_mod.append("waist=\n")
            profile_mod.append("legs=\n")
            profile_mod.append("feet=\n")
            profile_mod.append("finger1=\n")
            profile_mod.append("finger2=\n")
        if( disable_weapon_effects ):
            profile_mod.append(f"main_hand={switch_weapon()}\n")
        sim_profile.write("\n")
        for i in profile_mod:
            sim_profile.write(i)

profile = f"{sim_class}_{specilization}_input.simc"

match platform.system():
    case "Windows":
        main_string = os.path.join(simc_dir, "simc.exe") + " " + os.path.join(profile_dir, profile) + " dps_plot_stat="
    case "Linux":
        main_string = os.path.join(simc_dir, "simc") + " " + os.path.join(profile_dir, profile) + " dps_plot_stat="
    case "Darwin":
        main_string = os.path.join(simc_dir, "simc") + " " + os.path.join(profile_dir, profile) + " dps_plot_stat="

stats = ['haste', 'crit', 'mastery', 'versatility', switch_primary()]
sim_stats = []
dont_sim_stats = []
sim_strings = {}
matrix_strings = {}
haste_matrix_stats = []
haste_matrix_gen_stats = []
crit_matrix_stats = []
crit_matrix_gen_stats = []
mastery_matrix_stats = []
mastery_matrix_gen_stats = []
vers_matrix_stats = []
vers_matrix_gen_stats = []
primary_matrix_stats = []
primary_matrix_gen_stats = []
sim_matrix_stats = []

if( sim_haste_matrix ):
    if( gen_crit_secondary_matrix ):
        haste_matrix_stats.append('crit')
        haste_matrix_gen_stats.append('crit')
    if( gen_mastery_secondary_matrix ):
        haste_matrix_stats.append('mastery')
        haste_matrix_gen_stats.append('mastery')
    if( gen_vers_secondary_matrix ):
        haste_matrix_stats.append('versatility')
        haste_matrix_gen_stats.append('versatility')
    if( gen_primary_secondary_matrix ):
        haste_matrix_stats.append(switch_primary())
        haste_matrix_gen_stats.append(switch_primary())
    sim_matrix_stats.append('haste')
else:
    if( gen_crit_secondary_matrix ):
        haste_matrix_gen_stats.append('crit')
    if( gen_mastery_secondary_matrix ):
        haste_matrix_gen_stats.append('mastery')
    if( gen_vers_secondary_matrix ):
        haste_matrix_gen_stats.append('versatility')
    if( gen_primary_secondary_matrix ):
        haste_matrix_gen_stats.append(switch_primary())

if( sim_crit_matrix ):
    if( gen_haste_secondary_matrix ):
        crit_matrix_stats.append('haste')
        crit_matrix_gen_stats.append('haste')
    if( gen_mastery_secondary_matrix ):
        crit_matrix_stats.append('mastery')
        crit_matrix_gen_stats.append('mastery')
    if( gen_vers_secondary_matrix ):
        crit_matrix_stats.append('versatility')
        crit_matrix_gen_stats.append('versatility')
    if( gen_primary_secondary_matrix ):
        crit_matrix_stats.append(switch_primary())
        crit_matrix_gen_stats.append(switch_primary())
    sim_matrix_stats.append('crit')
else:
    if( gen_haste_secondary_matrix ):
        crit_matrix_gen_stats.append('haste')
    if( gen_mastery_secondary_matrix ):
        crit_matrix_gen_stats.append('mastery')
    if( gen_vers_secondary_matrix ):
        crit_matrix_gen_stats.append('versatility')
    if( gen_primary_secondary_matrix ):
        crit_matrix_gen_stats.append(switch_primary())

if( sim_mastery_matrix ):
    if( gen_haste_secondary_matrix ):
        mastery_matrix_stats.append('haste')
        mastery_matrix_gen_stats.append('haste')
    if( gen_crit_secondary_matrix ):
        mastery_matrix_stats.append('crit')
        mastery_matrix_gen_stats.append('crit')
    if( gen_vers_secondary_matrix ):
        mastery_matrix_stats.append('versatility')
        mastery_matrix_gen_stats.append('versatility')
    if( gen_primary_secondary_matrix ):
        mastery_matrix_stats.append(switch_primary())
        mastery_matrix_gen_stats.append(switch_primary())
    sim_matrix_stats.append('mastery')
else:
    if( gen_haste_secondary_matrix ):
        mastery_matrix_gen_stats.append('haste')
    if( gen_crit_secondary_matrix ):
        mastery_matrix_gen_stats.append('crit')
    if( gen_vers_secondary_matrix ):
        mastery_matrix_gen_stats.append('versatility')
    if( gen_primary_secondary_matrix ):
        mastery_matrix_gen_stats.append(switch_primary())

if( sim_vers_matrix ):
    if( gen_haste_secondary_matrix ):
        vers_matrix_stats.append('haste')
        vers_matrix_gen_stats.append('haste')
    if( gen_crit_secondary_matrix ):
        vers_matrix_stats.append('crit')
        vers_matrix_gen_stats.append('crit')
    if( gen_mastery_secondary_matrix ):
        vers_matrix_stats.append('mastery')
        vers_matrix_gen_stats.append('mastery')
    if( gen_primary_secondary_matrix ):
        vers_matrix_stats.append(switch_primary())
        vers_matrix_gen_stats.append(switch_primary())
    sim_matrix_stats.append('versatility')
else:
    if( gen_haste_secondary_matrix ):
        vers_matrix_gen_stats.append('haste')
    if( gen_crit_secondary_matrix ):
        vers_matrix_gen_stats.append('crit')
    if( gen_mastery_secondary_matrix ):
        vers_matrix_gen_stats.append('mastery')
    if( gen_primary_secondary_matrix ):
        vers_matrix_gen_stats.append(switch_primary())

if( sim_primary_matrix ):
    if( gen_haste_secondary_matrix ):
        primary_matrix_stats.append('haste')
        primary_matrix_gen_stats.append('haste')
    if( gen_crit_secondary_matrix ):
        primary_matrix_stats.append('crit')
        primary_matrix_gen_stats.append('crit')
    if( gen_mastery_secondary_matrix ):
        primary_matrix_stats.append('mastery')
        primary_matrix_gen_stats.append('mastery')
    if( gen_vers_secondary_matrix ):
        primary_matrix_stats.append('versatility')
        primary_matrix_gen_stats.append('versatility')
    sim_matrix_stats.append(switch_primary())
else:
    if( gen_haste_secondary_matrix ):
        primary_matrix_gen_stats.append('haste')
    if( gen_crit_secondary_matrix ):
        primary_matrix_gen_stats.append('crit')
    if( gen_mastery_secondary_matrix ):
        primary_matrix_gen_stats.append('mastery')
    if( gen_vers_secondary_matrix ):
        primary_matrix_gen_stats.append('versatility')

if( len(sim_matrix_stats) == 0 ):
    if( sim_haste ):
        sim_stats.append('haste')
    else:
        dont_sim_stats.append('haste')
    if( sim_crit ):
        sim_stats.append('crit')
    else:
        dont_sim_stats.append('crit')
    if( sim_mastery ):
        sim_stats.append('mastery')
    else:
        dont_sim_stats.append('mastery')
    if( sim_vers ):
        sim_stats.append('versatility')
    else:
        dont_sim_stats.append('versatility')
    if( sim_primary ):
        sim_stats.append(switch_primary())
    else:
        dont_sim_stats.append(switch_primary())

layout = go.Layout(
    autosize=False,
    width=graph_width,
    height=graph_height
)

fig=go.Figure( layout=layout )

fight_type_string = ""
if( fight_style == "Patchwerk" ):
    if( desired_targets == 1 ):
        fight_type_string = "Single_Target"
    if( desired_targets > 1 ):
        fight_type_string = f"{desired_targets}_Target_AoE"
elif( fight_style == "DungeonSlice" ):
    fight_type_string = "Mixed_Target_Count"
else:
    fight_type_string = "Unknown_Target_Count"

def get_old_data( stat ):
    return pd.read_csv(os.path.join(data_dir, f"{sim_class}_{specilization}_{stat}_{fight_type_string}.csv"), skiprows=1)

def get_old_modified_data( stat ):
    return pd.read_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{stat}_{fight_type_string}_mod.csv") )

def get_old_matrix_data( stat, matrix_stat ):
    return pd.read_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_{matrix_stat}_{stat}_mod.csv") )

def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    set_prompt = " [y/n] "

    try:
        choice = inputimeout(prompt=question+set_prompt, timeout=10)
        if choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")
            query_yes_no(question, default)
    except TimeoutOccurred:
        return valid[default]
        
def get_stat_name( stat ):
    if( switch_primary() == stat ):
        stat_name = stat
    else:
        stat_name = f"{stat}_rating"
    return stat_name
    
def generate_extra_data( data, stat ):
    data['DPS change'] = ( data[' DPS'].diff() )
    data['Rating Change'] = ( data[get_stat_name(stat)].diff() )
    data['DPS per point'] = data['DPS change'] / data['Rating Change']
    data['Rolling DPS per point'] = data['DPS per point'].rolling(window=rolling_avg).mean()
    data.to_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{stat}_{fight_type_string}_mod.csv"), index=False)
    new_data = pd.read_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{stat}_{fight_type_string}_mod.csv"))
    add_data(new_data, stat)

def generate_matrix_data( data, matrix_stat, step, point, stat ):
    rating = step*point
    data['DPS change'] = ( data[' DPS'].diff() )
    data['Rating Change'] = ( data[get_stat_name(stat)].diff() )
    data['DPS per point'] = data['DPS change'] / data['Rating Change']
    data['Rolling DPS per point'] = data['DPS per point'].rolling(window=rolling_avg).mean()
    data[matrix_stat+' Rating'] = rating
    data['Average DPS per point'] = data['DPS per point'].mean()
    data['Average DPS'] = data[' DPS'].mean()
    indexrating = data[ (data[get_stat_name(stat)] > 0 )].index
    data.drop(indexrating, inplace=True)
    csv_header = True
    csv_mode = 'w'
    if( point > 0 ):
        csv_header = False
        csv_mode = 'a'
    data.to_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_{matrix_stat}_{stat}_mod.csv"), mode=csv_mode, header=csv_header, index=False)
    new_data = pd.read_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_{matrix_stat}_{stat}_mod.csv"))
    new_data['Pct increase'] = ( new_data['Average DPS'].diff() / new_data['Average DPS'] ) * 100
    new_data.to_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_{matrix_stat}_{stat}_mod.csv"), index=False)

def add_data( data, stat ):
    if( graph_dps_per_point == True ):
        fig.add_trace(go.Scatter(x=data[get_stat_name(stat)], y=data['Rolling DPS per point'], mode=graph_style, name=get_stat_name(stat)))
    if( graph_dps == True ):
        fig.add_trace(go.Scatter(x=data[get_stat_name(stat)], y=data[' DPS'], mode=graph_style, name=get_stat_name(stat)))
    data.describe(include='all').to_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{stat}_{fight_type_string}_data_info.csv"), index=True)

def add_matrix_data( data, matrix_stat, stat ):
    fig.add_trace(go.Scatter(x=data[f'{matrix_stat} Rating'], y=data['Pct increase'], mode=graph_style, name=stat))
    data.describe(include='all').to_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_{matrix_stat}_{stat}_data_info.csv"), index=True)

graph_type_string = ""
if( graph_dps_per_point == True ):
    graph_type_string = "DPS per point"
if( graph_dps == True ):
    graph_type_string = "DPS"

def generate_chart():
    fig.update_layout(title=f'{sim_duration} second {fight_type_string} - {specilization} {sim_class} - {graph_type_string} vs Rating', xaxis_title='Stat Rating', yaxis_title=f'{graph_type_string}')
    fig.write_image(os.path.join(chart_output_dir,f'{sim_class}_{specilization}_{fight_type_string}_{graph_type_string}.png'))
    if( graph_open ):
        fig.show()
    fig.data = []

def generate_matrix_chart( stat ):
    fig.update_layout(title=f'{sim_duration} second {fight_type_string} - {specilization} {sim_class} - {graph_type_string} vs {stat} Rating', xaxis_title=f'{stat} Rating', yaxis_title=f'{graph_type_string}')
    fig.write_image(os.path.join(chart_output_dir, f'{sim_class}_{specilization}_{stat}_matrix_{fight_type_string}_{graph_type_string}.png'))
    if( graph_open ):
        fig.show()
    fig.data = []


def matrix_sim_finished( matrix_stat, stat ):
    new_data = pd.read_csv(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_{matrix_stat}_{stat}_mod.csv"))
    add_matrix_data(new_data, matrix_stat, stat)

def run_stat_sim( stat ):
    sim_strings[stat] = main_string+stat+" reforge_plot_output_file="+os.path.join(data_dir, f"{sim_class}_{specilization}_{stat}_{fight_type_string}.csv")
    print(sim_strings[stat])
    return_stat = subprocess.call(sim_strings[stat].split())
    if( return_stat == 0 ):
        sim_input=pd.read_csv(os.path.join(data_dir, f"{sim_class}_{specilization}_{stat}_{fight_type_string}.csv"), skiprows=1)
        if( generate_stat_charts ):
            generate_extra_data( sim_input, stat )

def run_matrix_sim( matrix_stat, stat ):
    for i in range(matrix_points):
        matrix_strings[stat] = main_string+stat+" reforge_plot_output_file="+os.path.join(data_dir, f"{sim_class}_{specilization}_{fight_type_string}_{matrix_stat}_{stat}.csv")+f" gear_{get_stat_name(matrix_stat)}={i*matrix_step}"
        print(matrix_strings[stat])
        return_stat = subprocess.call(matrix_strings[stat].split())
        if( return_stat == 0 ):
            matrix_input=pd.read_csv(os.path.join(data_dir, f"{sim_class}_{specilization}_{fight_type_string}_{matrix_stat}_{stat}.csv"), skiprows=1)
            generate_matrix_data( matrix_input, matrix_stat, matrix_step, i, stat )

# Run the sim
for i in sim_stats:
    if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{i}_{fight_type_string}.csv"))):
        if( query_yes_no(f"Data already exists for {i}, would you like to run the sim anyway?", "yes") ):
            run_stat_sim(i)
        else:
            dont_sim_stats.append(i)
    else:
        run_stat_sim(i)

for q in haste_matrix_stats:
    if( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_haste_{q}_mod.csv") )):
        if( query_yes_no(f"Data already exists for haste/{q}, would you like to run the sim anyway?", "yes") ):
            run_matrix_sim('haste', q)
    else:
        run_matrix_sim('haste', q)
    
for q in crit_matrix_stats:
    if( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_crit_{q}_mod.csv") )):
        if( query_yes_no(f"Data already exists for crit/{q}, would you like to run the sim anyway?", "yes") ):
            run_matrix_sim('crit', q)
    else:
        run_matrix_sim('crit', q)

for q in mastery_matrix_stats:
    if( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_mastery_{q}_mod.csv") )):
        if( query_yes_no(f"Data already exists for mastery/{q}, would you like to run the sim anyway?", "yes") ):
            run_matrix_sim('mastery', q)
    else:
        run_matrix_sim('mastery', q)

for q in vers_matrix_stats:
    if( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_versatility_{q}_mod.csv") )):
        if( query_yes_no(f"Data already exists for vers/{q}, would you like to run the sim anyway?", "yes") ):
            run_matrix_sim('versatility', q)
    else:
        run_matrix_sim('versatility', q)

for q in primary_matrix_stats:
    if( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_{switch_primary()}_{q}_mod.csv") )):
        if( query_yes_no(f"Data already exists for {switch_primary()}/{q}, would you like to run the sim anyway?", "yes") ):
            run_matrix_sim(switch_primary(), q)
    else:
        run_matrix_sim(switch_primary(), q)

if( generate_stat_charts ):
    primary = switch_primary()
    for s in dont_sim_stats:
        match s:
            case "haste":
                if( graph_haste ):
                    if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}_mod.csv"))):
                        print("Adding modified haste data")
                        add_data( get_old_modified_data(s), s )
                    else:
                        if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}.csv"))):
                            generate_extra_data( get_old_data(s), s )
                            print("Adding haste data")
            case "crit":
                if( graph_crit ):
                    if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}_mod.csv"))):
                        add_data( get_old_modified_data(s), s )
                    else:
                        if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}.csv"))):
                            generate_extra_data( get_old_data(s), s )
            case "mastery":
                if( graph_mastery ):
                    if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}_mod.csv"))):
                        add_data( get_old_modified_data(s), s )
                    else:
                        if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}.csv"))):
                            generate_extra_data( get_old_data(s), s )
            case "versatility":
                if( graph_vers ):
                    if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}_mod.csv"))):
                        add_data( get_old_modified_data(s), s )
                    else:
                        if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}.csv"))):
                            generate_extra_data( get_old_data(s), s )
            case primary:
                if( graph_primary ):
                    if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}_mod.csv"))):
                        add_data( get_old_modified_data(s), s )
                    else:
                        if( os.path.isfile(os.path.join(data_dir, f"{sim_class}_{specilization}_{s}_{fight_type_string}.csv"))):
                            generate_extra_data( get_old_data(s), s )
    generate_chart()

if( generate_matrix_charts ):
    for i in haste_matrix_gen_stats:
        if ( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_haste_{i}_mod.csv"))):
            matrix_sim_finished( "haste", i )
        if i == str(haste_matrix_gen_stats[-1]):
            generate_matrix_chart( 'haste' )
    for i in crit_matrix_gen_stats:
        if ( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_crit_{i}_mod.csv"))):
            matrix_sim_finished( "crit", i )
        if i == str(crit_matrix_gen_stats[-1]):
            generate_matrix_chart( 'crit' )
    for i in mastery_matrix_gen_stats:
        if( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_mastery_{i}_mod.csv"))):
            matrix_sim_finished( "mastery", i )
        if i == str(mastery_matrix_gen_stats[-1]):
            generate_matrix_chart( 'mastery' )
    for i in vers_matrix_gen_stats:
        if( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_versatility_{i}_mod.csv"))):
            matrix_sim_finished( "versatility", i )
        if i == str(vers_matrix_gen_stats[-1]):
            generate_matrix_chart( 'versatility' )
    for i in primary_matrix_gen_stats:
        if( os.path.isfile(os.path.join(output_dir, f"{sim_class}_{specilization}_{fight_type_string}_{switch_primary()}_{i}_mod.csv"))):
            matrix_sim_finished( switch_primary(), i )
        if i == str(primary_matrix_gen_stats[-1]):
            generate_matrix_chart( switch_primary() )
                