# 2024/4/16
# arm length = 0.25 torque = xxxxxxxxx

import matplotlib.pyplot as plt
import numpy as np
import math

# for accuracy plots
error_x_list = []
error_y_list = []
error_a_list = []



wind_active = True  # Activate wind influence if set to True
group_number = 16  # Identifier for group assignment or documentation purposes

# PID controller's initial parameters and state
# when pi/18
pid_params = {
    'kp_x': 4.5, 'ki_x': 0, 'kd_x': 3.83,  # PID constants for X direction
    'kp_yy': 1.5,  # Proportional gain for intermediate velocity calculation in Y
    'kp_y': 8, 'ki_y': 0, 'kd_y': 0.1,  # PID constants for Y direction
    'kp_a': 0.3, 'ki_a': 0.00, 'kd_a': 0.6,  # PID constants for angular adjustments
}

# Cumulative errors and last errors for integral and derivative calculations
pid_state = {
    'integral_x': 0.0, 'prev_error_x': 0.0,
    'integral_y': 0.0, 'prev_error_y': 0.0,
    'integral_a': 0.0, 'prev_error_a': 0.0,
}


def controller(state, target_pos, dt):
    # #     # state format: [position_x (m), position_y (m), velocity_x (m/s), velocity_y (m/s), attitude(radians), angular_velocity (rad/s)]
    # #     # target_pos format: [x (m), y (m)]
    # #     # dt: time step
    # #     # return: action format: (u_1, u_2)
    # #     # u_1 and u_2 are the throttle settings of the left and right motor
    error_x = target_pos[0] - state[0]  # Error in X direction
    error_yy = target_pos[1] - state[1]  # Intermediate target for Y velocity calculation

    # Update integrals and derivatives for PID calculations
    pid_state['integral_x'] += error_x * dt
    derivative_x = (error_x - pid_state['prev_error_x']) / dt

    desired_vel_y = pid_params['kp_yy'] * error_yy  # Desired Y velocity from proportional gain
    error_y = desired_vel_y - state[3]  # Actual error in Y direction
    pid_state['integral_y'] += error_y * dt
    derivative_y = (error_y - pid_state['prev_error_y']) / dt

    # Calculate PID outputs for X and Y directions
    output_x = pid_params['kp_x'] * error_x + pid_params['ki_x'] * pid_state['integral_x'] + pid_params['kd_x'] * derivative_x
    output_y = pid_params['kp_y'] * error_y + pid_params['ki_y'] * pid_state['integral_y'] + pid_params['kd_y'] * derivative_y

    # Desired attitude calculation based on PID output for X-axis
    max_attitude = math.pi / 18  # Maximum attitude adjustment
    desired_attitude = max_attitude * math.tanh(output_x)  # Use tanh to limit the output within the range

    error_a = desired_attitude - state[4]  # Attitude error calculation

    pid_state['integral_a'] += error_a * dt
    derivative_a = (error_a - pid_state['prev_error_a']) / dt
    output_a = pid_params['kp_a'] * error_a + pid_params['ki_a'] * pid_state['integral_a'] + pid_params['kd_a'] * derivative_a

    pid_state['prev_error_x'] = error_x
    pid_state['prev_error_y'] = error_y
    pid_state['prev_error_a'] = error_a

    u_1 = 0.41 - output_y + output_a  # Calculate control output for left motor
    u_2 = 0.41 - output_y - output_a  # Calculate control output for right motor

    u_1 = max(0, min(1, u_1))  # Ensure control outputs are within the bounds [0,1]
    u_2 = max(0, min(1, u_2))

    # Output debugging information to help during development or testing
    print(
        f"Error X: {error_x}, Desired Attitude: {desired_attitude}, Error Y: {error_y}, Error a: {error_a}, Output X: {output_x}, Output Y: {output_y}, U1: {u_1}, U2: {u_2}")

    #for accuracy plots
    '''
    time = np.arange(0,15,dt)


    global error_x_list, error_a_list, error_y_list
    error_x_list.append(error_x)
    error_y_list.append(error_y)
    error_a_list.append(error_a)
    
    if len(error_x_list) == len(time):    
        plt.plot(time,error_x_list, label='x')
        plt.xlabel('Time (s)')
        plt.ylabel('Error in x (m)')
        plt.title('Error in X vs Time')
        plt.legend()
        plt.show()

    if len(error_y_list) == len(time):    
        plt.plot(time,error_y_list, label='y')
        plt.xlabel('Time (s)')
        plt.ylabel('Error in y (m)')
        plt.title('Error in Y vs Time')
        plt.legend()
        plt.show()

    if len(error_a_list) == len(time):    
        plt.plot(time,error_a_list, label='a')
        plt.xlabel('Time (s)')
        plt.ylabel('Error in a (m)')
        plt.title('Error in A vs Time')
        plt.legend()
        plt.show()
    '''
    return (u_1, u_2)

