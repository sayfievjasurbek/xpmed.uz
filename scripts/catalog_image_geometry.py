"""Native image resolution follows transformed source axes, including 90° rotations."""
import math

def native_image_dpi(info):
    a,b,c,d,_,_=info['transform']
    x_axis=math.hypot(a,b);y_axis=math.hypot(c,d)
    if not x_axis or not y_axis:
        raise ValueError('Degenerate image transform')
    return 72*max(info['width']/x_axis,info['height']/y_axis)
