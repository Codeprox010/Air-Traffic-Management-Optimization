#!/usr/bin/env python3
import numpy as np
import random
import matplotlib.pyplot as plt

def compute_velocity(altitudes, alpha=1.0, gamma=1.0):
    velocity = np.zeros_like(altitudes)

    for i, h in enumerate(altitudes):
        if h >= 8000:
            velocity[i] = (235 - 5 * ((11000 - h) / 1000)) * alpha

        elif h >= 3500:
            velocity[i] = (200 - 12 * ((8000 - h) / 1000)) * gamma


        elif h >= 2000:
            velocity[i] = 150 - 20 * ((4000 - h) / 1000)

        else:
            velocity[i] = 75.0

    return velocity



def wind_params_A320():
    wind_speed=random.uniform(-22,22)
    ground_speed = 240 + wind_speed
    t_time=669600/ground_speed
    return t_time,ground_speed

phase_inputs = [
        {"phase": "Taxi-IN",   "Altitude": 0,     "speed": 7,   "time": 60, "rho": 1.229},
        {"phase": "Take off",  "Altitude": 500,   "speed": 75,  "time": 60, "rho": 0.9},
        {"phase": "Climb",     "Altitude": 11000, "speed": 200, "time": 1100},
        {"phase": "Cruise",    "Altitude": 11000, "speed": 240, "time": 2710 ,"rho": 0.36},
        {"phase": "Descent",   "Altitude": 300,    "speed": 150, "time": 1350},
        {"phase": "Approach",  "Altitude": 0,     "speed": 75,  "time": 100, "rho": 0.9},
        {"phase": "Taxi-OUT",  "Altitude": 0,     "speed": 10,  "time": 60, "rho": 1.229},
    ]

custom_inputs=phase_inputs.copy()


def run_A320(time,cruise_Speed):
    global Emissions_list,phase_inputs
    if cruise_Speed==0:
        phase_inputs = [{"phase": "Taxi-OUT",  "Altitude": 0,"speed": 10,  "time": 60, "rho": 1.229}]
    else:
        phase_inputs[3]['time']=669600/cruise_Speed
    TSFC_dict = {
        "Taxi-IN": 0.0000070,
        "Take off": 0.0000095,
        "Climb": 0.0000091,
        "Cruise": 0.0000079 ,
        "Descent": 0.0000072,
        "Approach": 0.0000068,
        "Taxi-OUT": 0.0000070
    }


    g,T_0,P_0,L,M,R=9.81,288.15,101325,0.0065,0.028,8.314
    mass = 75000    
    Wing_Area = 122.6
    k = 0.05
    W=mass*g
    Emissions=0
    Emissions_list=[]

    def compute_density(Altitude):
        T = T_0 - L * Altitude
        P = P_0 * (1 - (L * Altitude) / T_0) ** ((g * M) / (R * L))
        return (P * M) / (R * T)

    h,t=0,0
    for phase in phase_inputs:
            Altitude, Speed, time_phase = phase["Altitude"], phase["speed"], phase["time"] 
            TSFC = TSFC_dict[phase['phase']]
            
            if phase['phase'] in ['Taxi-IN', 'Taxi-OUT']:
                mu = 0.02
                D = mu * W
                MFR = D * TSFC
                if time<=t+time_phase:
                    Emissions= MFR*(time-t)*3.16
                    Emissions_list.append(Emissions)
                    if len(phase_inputs)==1:phase_inputs=custom_inputs
                    return sum(Emissions_list)
                                
                else:               
                    Emissions = MFR * time_phase * 3.16
                    Emissions_list.append(Emissions)
                    #print("TAXI EMISSIONS")
                t+=phase['time']

            elif phase['phase'] not in ['Descent', 'Climb']:
                rho=phase['rho']
                C_l=2*W/(rho*Speed**2*Wing_Area)
                C_D=0.025+k*C_l**2
                D=0.5*rho*Speed**2*Wing_Area*C_D

                MFR=D*TSFC
                if phase['phase']=='Cruise': 
                    #print("THE SPEED FOR EMISSION IN CRUISE PHASE",phase['speed'])
                    MFR*=1.4
                if time<=t+time_phase:
                    Emissions= MFR*(phase_inputs[3]['time'])*3.16
                    Emissions_list.append(Emissions)
                    return sum(Emissions_list)
                else:               
                    Emissions = MFR * time_phase * 3.16
                    Emissions_list.append(Emissions)
                t+=phase['time']

            else:
                altitudes = np.linspace(11000, Altitude,500)
                Speed=compute_velocity(altitudes)

                if phase['phase']=="Descent": 
                    Distance=phase['time']*Speed/500
                    Average_speed=np.sum(Speed)/500
                    TSFC = np.full(500, 0.0000072)
                F=(2*W/(Speed**2*Wing_Area))
                rho=compute_density(altitudes)
                C_l=F*rho
                C_D=(C_l*C_l)*k+0.025
                D = 0.5 * rho * Speed**2 * Wing_Area * C_D  
                MFR=D*TSFC
                if time<=t+time_phase:
                    Emissions_array=MFR*((time-t)/500)*3.16
                    phase_Emissions=np.sum(Emissions_array)
                    Emissions_list.append(phase_Emissions)
                    return sum(Emissions_list)
                else:               
                    Emissions_array=MFR*(time_phase/500)*3.16
                    phase_Emissions=np.sum(Emissions_array)
                    Emissions_list.append(phase_Emissions)
                t+=phase['time']
                h+=1


if __name__=='__main__':
    time2,cruise_Speed2=wind_params_A320()
    n=run_A320(time2+2425,240)
    print(cruise_Speed2)
    print(n)