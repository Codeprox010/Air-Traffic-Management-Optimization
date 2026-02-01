from TQM.A320 import *
from TQM.Boeing_737_800 import *
from TQM.path_planner_redefined import path_planner_redfined



def Drag(time,cruise_Speed):
        C_l=33258.74/cruise_Speed**2
        C_D=0.025+0.05*C_l**2
        D=0.18*cruise_Speed**2*122.9*C_D
        MFR=D*0.0000079*1.4
        return MFR*time*3.16
       
       
def main():
        e_A320_path_stats=0
        Emissions=0
        t_elapsed=3600
        t_time_A,cruise_Speed_A=wind_params_A320()
        e_A320_stats=run_A320(1120+t_time_A,cruise_Speed_A)
        t_time_B,cruise_Speed_B=wind_params_737()
        a_TIME=2455+t_time_A
        b_TIME=2255+t_time_B
        t=t_time_A-t_time_B
        rem_t_cruise=t_time_A+1120-t_elapsed

        if t<0:
              if t<-200:
                   e_A320_path_stats=0 
                   print('SKIPPED-AIRBUS WELL AHEAD NO NEED CDA',end=' ')     
              else:
                    print("AIRBUS AHEAD CASE",end=" ")
                    e_A320_path_stats=path_planner_redfined(1530+t,220000,11000,2.3)

        else:
              if t>200:
                   e_A320_path_stats=0
                   print('SKIPPED-BOEING WELL AHEAD NO NEED CDA',end=' ')
              else:
                    print("BOEING AHEAD CASE",end=" ")
                    e_A320_path_stats=path_planner_redfined(1530-t,220000,11000,2.3)
      



        e_A320_rem_stats=run_A320(60,0)
        e_A320_nonCDA_stats=run_A320(a_TIME,cruise_Speed_A)
        
        
        total_stats=e_A320_stats+e_A320_path_stats+e_A320_rem_stats+Emissions
        if e_A320_path_stats==0:total_stats=e_A320_nonCDA_stats
        #print('NOCDA',e_A320_nonCDA_stats,total_stats)
        #print('diff',d,e_A320_path_stats)
        #print('Total A320 Emissions:',total_stats)
        print('Emission reduction %:',((e_A320_nonCDA_stats-total_stats)/e_A320_nonCDA_stats)*100)


if __name__=='__main__':
    for _ in range(100):
      main()