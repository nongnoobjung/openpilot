from common.numpy_fast import clip, interp
from selfdrive.config import Conversions as CV
from cereal import car

# kph
V_CRUISE_MAX = 135
V_CRUISE_MIN = 5
V_CRUISE_DELTA = 5
V_CRUISE_ENABLE_MIN = 40
MPC_N = 16
CAR_ROTATION_RADIUS = 0.0
ACC_FAST_MODE = False

class MPC_COST_LAT:
  PATH = 1.0
  HEADING = 1.0
  STEER_RATE = 1.0


class MPC_COST_LONG:
  TTC = 5.0
  DISTANCE = 0.1
  ACCELERATION = 10.0
  JERK = 20.0


def rate_limit(new_value, last_value, dw_step, up_step):
  return clip(new_value, last_value + dw_step, last_value + up_step)


def get_steer_max(CP, v_ego):
  return interp(v_ego, CP.steerMaxBP, CP.steerMaxV)


def update_v_cruise(v_cruise_kph, buttonEvents, enabled, cur_time, accel_pressed,decel_pressed,accel_pressed_last,decel_pressed_last):
  
  if enabled:
    #if (accel_pressed and ((cur_time - accel_pressed_last) >= 1 or (ACC_FAST_MODE and (cur_time - accel_pressed_last) >= 0.5))):
      #ACC_FAST_MODE = True
      #v_cruise_kph += V_CRUISE_DELTA - (v_cruise_kph % V_CRUISE_DELTA)
    #elif (decel_pressed and ((cur_time - decel_pressed_last) >= 1 or (ACC_FAST_MODE and (cur_time - decel_pressed_last) >= 0.5))):
      #ACC_FAST_MODE = True
      #v_cruise_kph -= V_CRUISE_DELTA - ((V_CRUISE_DELTA - v_cruise_kph) % V_CRUISE_DELTA)
    #else:
    for b in buttonEvents:
      if not b.pressed:
        if b.type == car.CarState.ButtonEvent.Type.accelCruise:
          ACC_FAST_MODE = False
          #if (cur_time - accel_pressed_last) < 1:
          v_cruise_kph += 1
        elif b.type == car.CarState.ButtonEvent.Type.decelCruise:
          ACC_FAST_MODE = False
          #if (cur_time - decel_pressed_last) < 1:
          v_cruise_kph -= 1
    v_cruise_kph = clip(v_cruise_kph, V_CRUISE_MIN, V_CRUISE_MAX) 
  else:
    ACC_FAST_MODE = False 

  return v_cruise_kph


def initialize_v_cruise(v_ego, buttonEvents, v_cruise_last):
  for b in buttonEvents:
    # 250kph or above probably means we never had a set speed
    if b.type == car.CarState.ButtonEvent.Type.accelCruise and v_cruise_last < 250:
      return v_cruise_last

  return int(round(clip(v_ego * CV.MS_TO_KPH, V_CRUISE_ENABLE_MIN, V_CRUISE_MAX)))
