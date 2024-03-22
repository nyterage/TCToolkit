#!/usr/bin/env python3
import subprocess
import pandas as pd
import plotly.graph_objects as go
import os
import sys
import platform

# Input Variables
input_profile = "unh_tst.simc" # This should be a bare profile, only character info and gear
sim_class = "death_knight"
specilization = "unholy"
tar_err = 0.05 # Sims target Error
iter = 15000 # Max number of Iterations to run, will stop at this number if target error has not been reached
pos = 1 # Plot only positive values from the current rating, set to 0 to generate both positive and negative values
plot_step = 10 # Difference in Rating between each plot point
plot_points = 1000 # Number of plot points to generate
rolling_avg = 10 # Rolling average for DPS per point, set to 1 to disable rolling average
report_details = 1
optimal_raid = 1

# Profile Modifications
modify_base_profile = True # Set to False if you dont want to modify the base profile with the values below
tier_set_bonus = False
tier_set_bonus_2pc = 0
tier_set_bonus_4pc = 0
tier_set_number = 31
base_haste_rating = 0 # Set to 0 to set haste in the input ptofile to 0, otherwise set whatever value you wish
base_crit_rating = 0 # Set to 0 to set crit in the input ptofile to 0, otherwise set whatever value you wish
base_mastery_rating = 0 # Set to 0 to set mastery in the input ptofile to 0, otherwise set whatever value you wish
base_versatility_rating = 0 # Set to 0 to set versatility in the input ptofile to 0, otherwise set whatever value you wish
potion = "disabled"
food = "disabled"
flask = "disabled"
augmentation = "disabled"
temporary_enchants = False
temporary_enchant_disable_string = "disabled"
temporary_enchant_mh = "howling_rune_3"
temporary_enchant_oh = "howling_rune_3"

# Simulation Variables
sim_haste = True
sim_crit = True
sim_mastery = True
sim_vers = True
sim_primary = False

# Graph Variables
generate_charts = True
graph_haste = True
graph_crit = True
graph_mastery = True
graph_vers = True
graph_primary = False
# Only One of these two should be enabled at any one point in time!
graph_dps_per_point = True # Probably the only useful graph of the bunch
graph_dps = False # Plots DPS vs Rating, same thing youd get in the simc html output but bigger!

# --------------------------------------------------------------------------------------
# Code Starts Here, dont touch anything below this line unless you know what youre doing
# --------------------------------------------------------------------------------------
# Directories
profile_dir = str(os.path.dirname(os.path.realpath(sys.argv[0])))+"\\profiles\\"
simc_dir = str(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'simc')))
data_dir = str(os.path.dirname(os.path.realpath(sys.argv[0])))+"\\raw_data\\"
output_dir = str(os.path.dirname(os.path.realpath(sys.argv[0])))+"\\output\\"

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

# Lists of elements to add to the simc profile
sim_mod = []
profile_mod = []

base_profile = open(profile_dir+input_profile, "r")

sim_mod.append("target_error="+str(tar_err)+"\n")
sim_mod.append("report_details="+str(report_details)+"\n")
sim_mod.append("optimal_raid="+str(optimal_raid)+"\n")
sim_mod.append("dps_plot_iterations="+str(iter)+"\n")
sim_mod.append("dps_plot_points="+str(plot_points)+"\n")
sim_mod.append("dps_plot_step="+str(plot_step)+"\n")
sim_mod.append("dps_plot_positive="+str(pos)+"\n")
sim_mod.append("iterations="+str(iter)+"\n")
sim_mod.append("html="+output_dir+"output.html\n")
sim_mod.append("json2="+output_dir+"output.json\n")

with open(profile_dir+"input.simc", "w+") as sim_profile:
    for i in sim_mod:
        sim_profile.write(i)
    sim_profile.write("\n")
    sim_profile.write(base_profile.read())
    base_profile.close()
    if( modify_base_profile ):
        profile_mod.append("potion="+potion+"\n")
        profile_mod.append("food="+food+"\n")
        profile_mod.append("flask="+flask+"\n")
        profile_mod.append("augmentation="+augmentation+"\n")
        if( temporary_enchants == False ):
            profile_mod.append("temporary_enchant="+temporary_enchant_disable_string+"\n")
        else:
            profile_mod.append("temporary_enchant=main_hand:"+temporary_enchant_mh+"/"+"off_hand:"+temporary_enchant_oh+"\n")
        profile_mod.append("gear_crit_rating="+str(base_crit_rating)+"\n")
        profile_mod.append("gear_haste_rating="+str(base_haste_rating)+"\n")
        profile_mod.append("gear_mastery_rating="+str(base_mastery_rating)+"\n")
        profile_mod.append("gear_versatility_rating="+str(base_versatility_rating)+"\n")
        if( tier_set_bonus == False ):
            profile_mod.append("set_bonus=tier"+str(tier_set_number)+"_2pc="+str(tier_set_bonus_2pc)+"\n")
            profile_mod.append("set_bonus=tier"+str(tier_set_number)+"_4pc="+str(tier_set_bonus_4pc)+"\n")
        sim_profile.write("\n")
        for i in profile_mod:
            sim_profile.write(i)

profile = "input.simc"

stats = ["haste", "crit", "mastery", "versatility"]
if( sim_primary ):
    stats.append(switch_primary())

match platform.system():
    case "Windows":
        main_string = simc_dir+"\\simc.exe "+profile_dir+profile+" dps_plot_stat="
    case "Linux":
        main_string = simc_dir+"/simc "+profile_dir+profile+" dps_plot_stat="
    case "Darwin":
        main_string = simc_dir+"/simc "+profile_dir+profile+" dps_plot_stat="

for i in stats:
    match i:
        case "haste":
            haste_input_string = main_string+i+" reforge_plot_output_file="+data_dir+i+".csv"
        case "crit":
            crit_input_string = main_string+i+" reforge_plot_output_file="+data_dir+i+".csv"
        case "mastery":
            mastery_input_string = main_string+i+" reforge_plot_output_file="+data_dir+i+".csv"
        case "versatility":
            vers_input_string = main_string+i+" reforge_plot_output_file="+data_dir+i+".csv"
        case "strength":
            str_input_string = main_string+i+" reforge_plot_output_file="+data_dir+i+".csv"
        case "agility":
            agi_input_string = main_string+i+" reforge_plot_output_file="+data_dir+i+".csv"
        case "intellect":
            int_input_string = main_string+i+" reforge_plot_output_file="+data_dir+i+".csv"


fig=go.Figure()

def get_old_data( stat ):
    if( stat == 'haste' ):
        if ( sim_haste == False ):
            return pd.read_csv(data_dir+stat+'.csv', skiprows=1)
    if( stat == 'crit' ):
        if ( sim_crit == False ):
            return pd.read_csv(data_dir+stat+'.csv', skiprows=1)
    if( stat == 'mastery' ):
        if ( sim_mastery == False ):
            return pd.read_csv(data_dir+stat+'.csv', skiprows=1)
    if( stat == 'versatility' ):
        if ( sim_vers == False ):
            return pd.read_csv(data_dir+stat+'.csv', skiprows=1)
    if( stat == 'strength' ):
        if ( sim_primary == False ):
            return pd.read_csv(data_dir+stat+'.csv', skiprows=1)
    if( stat == 'agility' ):
        if ( sim_primary == False ):
            return pd.read_csv(data_dir+stat+'.csv', skiprows=1)
    if( stat == 'intellect' ):
        if ( sim_primary == False ):
            return pd.read_csv(data_dir+stat+'.csv', skiprows=1)
        
def get_stat_name( stat ):
    match stat:
        case "haste":
            stat_name = "haste_rating"
        case "crit":
            stat_name = "crit_rating"
        case "mastery":
            stat_name = "mastery_rating"
        case "versatility":
            stat_name = "versatility_rating"
        case "strength":
            stat_name = "strength"
        case "agility":
            stat_name = "agility"
        case "intellect":
            stat_name = "intellect"
    return stat_name
    
def generate_extra_data( data, stat ):
    data['DPS change'] = ( data[' DPS'].diff() )
    data['Rating Change'] = ( data[get_stat_name(stat)].diff() )
    data['DPS per point'] = data['DPS change'] / data['Rating Change']
    data['Rolling DPS per point'] = data['DPS per point'].rolling(window=rolling_avg).mean()
    data.to_csv(output_dir+stat+'_mod.csv', index=False)
    new_data = pd.read_csv(output_dir+stat+'_mod.csv')
    add_data(new_data, stat)

def add_data( data, stat ):
    if( graph_dps_per_point == True ):
        fig.add_trace(go.Scatter(x=data[get_stat_name(stat)], y=data['Rolling DPS per point'], mode='lines+markers', name=get_stat_name(stat)))
    if( graph_dps == True ):
        fig.add_trace(go.Scatter(x=data[get_stat_name(stat)], y=data[' DPS'], mode='lines+markers', name=get_stat_name(stat)))
    data.describe(include='all').to_csv(output_dir+stat+'_data_info.csv', index=True)

def generate_chart():
    if( graph_dps_per_point == True ):
        fig.update_layout(title='DPS per point vs Rating', xaxis_title='Stat Rating', yaxis_title='DPS per point')
        fig.write_image(output_dir+'dps_per_point.png')
        fig.show()
    if( graph_dps == True ):
        fig.update_layout(title='DPS vs Rating', xaxis_title='Stat Rating', yaxis_title='DPS')
        fig.write_image(output_dir+'dps.png')
        fig.show()

# Run the sim
if( sim_haste ):
    print(haste_input_string.split())
    return_haste = subprocess.call(haste_input_string.split(), shell=True)
    if( return_haste == 0 ):
        haste_input=pd.read_csv(data_dir+'haste.csv', skiprows=1)
        if( graph_haste == True ):
            generate_extra_data( haste_input, 'haste')
if( sim_crit ):
    print(crit_input_string)
    return_crit = subprocess.call(crit_input_string.split(), shell=True)
    if( return_crit == 0 ):
        crit_input=pd.read_csv(data_dir+'crit.csv', skiprows=1)
        if( graph_crit == True ):
            generate_extra_data( crit_input, 'crit')
if( sim_mastery ):
    print(mastery_input_string)
    return_mastery = subprocess.call(mastery_input_string.split(), shell=True)
    if( return_mastery == 0 ):
        mastery_input=pd.read_csv(data_dir+'mastery.csv', skiprows=1)
        if( graph_mastery == True ):
            generate_extra_data( mastery_input, 'mastery')
if( sim_vers ):
    print(vers_input_string)
    return_vers = subprocess.call(vers_input_string.split(), shell=True)
    if( return_vers == 0 ):
        vers_input=pd.read_csv(data_dir+'versatility.csv', skiprows=1)
        if( graph_vers == True ):
            generate_extra_data( vers_input, 'versatility')
if( sim_primary ):
    if( switch_primary() == "strength" ):
        print(str_input_string)
        return_str = subprocess.call(str_input_string.split(), shell=True)
        if( return_str == 0 ):
            str_input=pd.read_csv(data_dir+'strength.csv', skiprows=1)
            if( graph_primary == True ):
                generate_extra_data( str_input, 'strength')
    if( switch_primary() == "agility" ):
        print(agi_input_string)
        return_agi = subprocess.call(agi_input_string.split(), shell=True)
        if( return_agi == 0 ):
            agi_input=pd.read_csv(data_dir+'agility.csv', skiprows=1)
            if( graph_primary == True ):
                generate_extra_data( agi_input, 'agility')
    if( switch_primary() == "intellect" ):
        print(int_input_string)
        return_int = subprocess.call(int_input_string.split(), shell=True)
        if( return_int == 0 ):
            int_input=pd.read_csv(data_dir+'intellect.csv', skiprows=1)
            if( graph_primary == True ):
                generate_extra_data( int_input, 'intellect')
if( generate_charts ):
    if( sim_haste == False ):
        if( graph_haste == True ):
            generate_extra_data( get_old_data('haste'), 'haste' )
    if( sim_crit == False ):
        if( graph_crit == True ):
            generate_extra_data( get_old_data('crit'), 'crit' )
    if( sim_mastery == False ):
        if( graph_mastery == True ):
            generate_extra_data( get_old_data('mastery'), 'mastery' )
    if( sim_vers == False ):
        if( graph_vers == True ):
            generate_extra_data( get_old_data('versatility'), 'versatility' )
    if( sim_primary == False ):
        if( graph_primary == True ):
            if( switch_primary() == "strength" ):
                generate_extra_data( get_old_data('strength'), 'strength' )
            if( switch_primary() == "agility" ):
                generate_extra_data( get_old_data('agility'), 'agility' )
            if( switch_primary() == "intellect" ):
                generate_extra_data( get_old_data('intellect'), 'intellect' )
    generate_chart()
