import matplotlib.pyplot as plt     # plotting
from scipy.optimize import minimize,NonlinearConstraint
import numpy as np
# main optimizer (L-BFGS-B, TNC, etc.)


def path_planner_redfined(descent_time,dist,cda_start_alt,theta_normal_deg=2.1):
    bounds = [(2.0, 3.0)]
    g,T_0,P_0,L,M,R=9.81,288.15,101325,0.0065,0.028,8.314
    mass = 75000    
    K_ind = 0.05
    W=mass*g
    Wing_Area = 122.6


    def AG_optimizer(theta, target_time, altitudes):
        best_alpha = None
        best_gamma = None
        best_time = None
        best_error = float("inf")


        for alpha in np.arange(0.9, 1.0, 0.01):
            for gamma in np.arange(0.9, 1.0, 0.01):

                t = descent_time_fn(theta, altitudes, alpha, gamma)

                err = abs(t - target_time)

                if err < best_error:
                    best_error = err
                    best_alpha = alpha
                    best_gamma = gamma
                    best_time = t
        #print(best_alpha, best_gamma, best_time, best_error)
        return best_alpha, best_gamma, best_time, best_error
    
    def descent_time_constraint(theta):
        theta_f = float(np.atleast_1d(theta)[0])
        t_normal = 0.0
        if len(altitudes_normal) > 1:
            t_normal = normal_descent_time(
                altitudes_normal,
                theta_normal_deg
            )

        # CDA must only satisfy the REMAINING time
        target_time_cda = target_time - t_normal

        alpha_best, gamma_best, t_cda, err = AG_optimizer(
            theta_f,
            target_time_cda,
            altitudes_cda
        )

        return t_normal + t_cda


    
    
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

    def compute_density(Altitude):
            T = T_0 - L * Altitude
            P = P_0 * (1 - (L * Altitude) / T_0) ** ((g * M) / (R * L))
            return (P * M) / (R * T)
    
    def horizontal_distance_fn(y,altitudes):
            dz = np.abs(np.diff(altitudes))
            theta=float(y)
            rad_y=np.deg2rad(theta)
            HD = np.sum(dz / np.tan(rad_y))
            return HD
    
    def horizontal_distance_normal(altitudes, theta_normal_deg):
        dz = np.abs(np.diff(altitudes))
        theta_normal = np.deg2rad(theta_normal_deg)
        return np.sum(dz / np.tan(theta_normal))

    
    def normal_descent_time(altitudes, theta_normal_deg):
        dz = np.abs(np.diff(altitudes))
        theta = np.deg2rad(theta_normal_deg)
        velocity = compute_velocity(altitudes)
        v_mid = 0.5 * (velocity[:-1] + velocity[1:])
        return np.sum(dz / (v_mid * np.sin(theta)))




    def descent_time_fn(x,altitudes,alpha,gamma):
        dz = np.abs(np.diff(altitudes))
        angle_rad = np.deg2rad(float(x))
        velocity2 = compute_velocity(altitudes, alpha=alpha, gamma=gamma)
        v_mid = 0.5 * (velocity2[:-1] + velocity2[1:])
        v_mid = np.maximum(v_mid, 1e-6)
        time = np.sum(dz / (v_mid * np.sin(angle_rad)))
        return time
    

    def normal_descent_emissions(altitudes):
        rho = compute_density(altitudes)
        velocity = compute_velocity(altitudes)  # no alpha/gamma
        theta = np.deg2rad(2.2)  # nominal descent angle

        F = (2 * W * np.cos(theta)) / (velocity**2 * Wing_Area)
        C_l = F * rho
        C_D = (C_l * C_l) * K_ind + 0.025
        D = 0.5 * rho * velocity**2 * Wing_Area * C_D

        TSFC_normal = 0.0000065
        MFR = D * TSFC_normal

        dz = np.abs(np.diff(altitudes))
        Emissions = MFR[:-1] * (dz / (velocity[:-1] * np.sin(theta))) * 3.16

        return np.sum(Emissions)


    def objective(x):
            
        # NORMAL PART
        E_normal = 0.0

        if len(altitudes_normal) > 1:
            E_normal = normal_descent_emissions(altitudes_normal)

        # CDA PART (your existing code)
        altitudes = altitudes_cda
        theta_deg = float(np.atleast_1d(x)[0])
        t_normal = 0.0
        if len(altitudes_normal) > 1:
            t_normal = normal_descent_time(altitudes_normal,theta_normal_deg  )

        target_time_cda = target_time - t_normal

        alpha_best, gamma_best, t_best, err = AG_optimizer(theta_deg,target_time_cda,altitudes)


        rho = compute_density(altitudes)
        velocity = compute_velocity(altitudes, alpha=alpha_best, gamma=gamma_best)
        theta = np.deg2rad(x)

        F = (2*W*np.cos(theta)/(velocity**2*Wing_Area))
        C_l = F * rho
        C_D = (C_l*C_l)*K_ind + 0.025
        D = 0.5 * rho * velocity**2 * Wing_Area * C_D

        #TSFC_high = 0.0000065
        #TSFC_array = np.where(velocity > 200, TSFC_high, TSFC)

        TSFC_normal=0.0000065
        TSFC_cda=0.0000045
        TSFC_array = np.where(altitudes > cda_start_alt,TSFC_normal,TSFC_cda)
        #print(velocity)
        MFR = D * TSFC_array
        dz = np.abs(np.diff(altitudes))
        E_cda = np.sum(MFR[:-1] * (dz / (velocity[:-1] * np.sin(theta))) * 3.16)

        return E_normal + E_cda
    altitudes_full = np.linspace(11000, 1500, 500)
    #print(altitudes_full)

    altitudes_normal = altitudes_full[altitudes_full >= cda_start_alt]
    altitudes_cda = altitudes_full[altitudes_full < cda_start_alt]

    target_time = descent_time  # e.g. 1385

    #print('descent_time',target_time)
    time_constraint = NonlinearConstraint(lambda x: descent_time_constraint(x), target_time-50, target_time + 50)

    target_dist = dist 
    HD_normal_real = 0.0
    if len(altitudes_normal) > 1:
        HD_normal_real = horizontal_distance_normal(altitudes_normal,theta_normal_deg)

    distance_constraint = NonlinearConstraint(lambda theta: HD_normal_real + horizontal_distance_fn(theta, altitudes_cda),target_dist - 4000, target_dist + 4000)


    result = minimize(objective, x0 = [2.3], bounds=bounds,constraints=[time_constraint,distance_constraint],method='SLSQP')
    print('success',result.success,end=' ')
    opt_dist = horizontal_distance_fn(result.x[0],altitudes_cda)
    theta_opt = result.x[0]


    HD_cda_real = horizontal_distance_fn(theta_opt, altitudes_cda)

    HD_total_real = HD_normal_real + HD_cda_real


    """print("HD:", opt_dist,end=' ')
    print(result)  
    print("Minimum Emissions:", result.fun)
    print("Optimal Angle:", result.x[0])
    print("Final x:", result.x)
    print("Descent time:", descent_time_constraint(result.x[0]))
    print("Target time bounds:", target_time-40, target_time+40)
    print("Horizontal distance:", HD_total_real)
    print("Target dist bounds:", target_dist-9000, target_dist+9000)"""

    return result.fun




if __name__=='__main__':
    path_planner_redfined(0,0)
