#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import random

def wind_params_737():
     global t_time,wind_speed
     wind_speed=random.uniform(-22,22)
     ground_speed = 240 + wind_speed
     t_time=640500//ground_speed
     return t_time,ground_speed

phase_inputs = [
    {"phase": "Taxi-OUT",  "Altitude": 0,      "speed": 7,     "time": 60,   "rho": 1.225},
    {"phase": "Take off",  "Altitude": 500,    "speed": 75,    "time": 60,    "rho": 1.1},
    {"phase": "Climb",     "Altitude": 11000,  "speed": 200,   "time": 1000},
    {"phase": "Cruise",    "Altitude": 11000,  "speed": 230,   "time": 2600,  "rho": 0.36},
    {"phase": "Descent",   "Altitude": 3000,   "speed": 190,   "time": 1000},
    {"phase": "Approach",  "Altitude": 0,      "speed": 75,    "time": 75,    "rho": 1.1},
    {"phase": "Taxi-IN",   "Altitude": 0,      "speed": 7,     "time": 60,   "rho": 1.225}
]



def run_737(time,cruise_Speed):
    global Emissions_list,phase_inputs
    if cruise_Speed!=0:
          phase_inputs[3]['speed']=240
          phase_inputs[3]['time']=669600//cruise_Speed
    else:
          phase_inputs = [
    {"phase": "Approach",  "Altitude": 0,      "speed": 75,    "time": 75,    "rho": 1.1},
    {"phase": "Taxi-IN",   "Altitude": 0,      "speed": 7,     "time": 60,   "rho": 1.225}
]
          

    TSFC_dict = {
        "Taxi-IN": 0.0000066,
        "Take off": 0.0000096,
        "Climb": 0.0000089,
        "Cruise": 0.0000077,
        "Descent": 0.0000060,
        "Approach": 0.0000069,
        "Taxi-OUT": 0.0000066
    }

    g,T_0,P_0,L,M,R=9.81,288.15,101325,0.0065,0.028,8.314
    mass = 78000
    Wing_Area = 124.6
    k = 0.048
    W=mass*g
    Emissions=0
    Emissions_list=[]


    def compute_density(Altitude):
        T = T_0 - L * Altitude
        P = P_0 * (1 - (L * Altitude) / T_0) ** ((g * M) / (R * L))
        return (P * M) / (R * T)

    t,h=0,0
    for phase in phase_inputs:
        Altitude, Speed, time_phase = phase["Altitude"], phase["speed"], phase["time"] 
        phase_inputs[3]['time']=time-2495
        TSFC = TSFC_dict[phase['phase']]

        if phase['phase'] in ['Taxi-IN', 'Taxi-OUT']:
            mu = 0.02
            D = mu * W
            MFR = D * TSFC
            if time<=t+time_phase:
                     Emissions= MFR*(time-t)*3.16
                     Emissions_list.append(Emissions)
                     return sum(Emissions_list)
            else:               
                     Emissions = MFR * time_phase * 3.16
                     Emissions_list.append(Emissions)
            t+=phase['time']
        elif phase['phase'] not in ['Descent', 'Climb']:
            rho=phase['rho']
            C_l=2*W/(rho*Speed**2*Wing_Area)
            C_D=0.024+k*C_l**2
            D=0.5*rho*Speed**2*Wing_Area*C_D
            MFR=D*TSFC
            if phase['phase']=='Cruise': MFR*=1.3
            if time<=t+time_phase:
                     Emissions= MFR*(phase_inputs[3]['time'])*3.16
                     Emissions_list.append(Emissions)
                     return sum(Emissions_list)
            else:               
                     Emissions = MFR * time_phase * 3.16
                     Emissions_list.append(Emissions)
            t+=phase['time']
        else:
            B_Alt=phase_inputs[h-1]['Altitude']
            F=(2*W/(Speed**2*Wing_Area))
            altitudes = np.linspace(B_Alt, Altitude,300)
            rho=compute_density(altitudes)
            C_l=F*rho
            C_D=(C_l*C_l)*k+0.024
            D = 0.5 * rho * Speed**2 * Wing_Area * C_D  # fully vectorized
            MFR=D*TSFC
            if time<=+time_phase:
                     Emissions_array=MFR*((time-t)/300)*3.16
                     phase_Emissions=np.sum(Emissions_array)
                     Emissions_list.append(phase_Emissions)
                     return sum(Emissions_list)
            else:               
                     Emissions_array=MFR*(time_phase/300)*3.16
                     phase_Emissions=np.sum(Emissions_array)
                     Emissions_list.append(phase_Emissions)
            t+=phase['time']
        h+=1


if __name__=='__main__':
   time2,cruise_Speed2=wind_params_737()
   n=run_737(time2+2495,cruise_Speed2)
   