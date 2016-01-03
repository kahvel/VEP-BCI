import constants as c


class BruteForce(object):
    def __init__(self):
        self.windows = [c.WINDOW_NONE, c.WINDOW_HANNING, c.WINDOW_HAMMING, c.WINDOW_BLACKMAN, c.WINDOW_BARTLETT]
        self.interpolation = [c.INTERPOLATE_LINEAR, c.INTERPOLATE_NEAREST, c.INTERPOLATE_ZERO, c.INTERPOLATE_SLINEAR, c.INTERPOLATE_QUADRATIC, c.INTERPOLATE_CUBIC, c.INTERPOLATE_BARYCENTRIC]
        self.detrend = [c.LINEAR_DETREND, c.CONSTANT_DETREND, c.NONE_DETREND]
        self.length_range = tuple(16*2**i for i in range(6))  # (16, 512)
        self.step_range = tuple(16*2**i for i in range(6))
        self.break_range = tuple(i for i in range(0, 33, 4))

    def optionsGenerator(self):
        for window in self.windows:
            for interpolation in self.interpolation:
                for detrend in self.detrend:
                    for length in self.length_range:
                        for step in self.step_range:
                            if step <= length:
                                for b in self.break_range:
                                    if b == 0 or length/b >= 16:
                                        yield {
                                            c.OPTIONS_WINDOW: window,
                                            c.OPTIONS_INTERPOLATE: interpolation,
                                            c.OPTIONS_DETREND: detrend,
                                            c.OPTIONS_LENGTH: length,
                                            c.OPTIONS_STEP: step,
                                            c.OPTIONS_BREAK: b,
                                            c.OPTIONS_FILTER: c.NONE_FILTER,
                                            c.OPTIONS_NORMALISE: 0,
                                            c.OPTIONS_ARG: 0,
                                        }
                                    else:
                                        break
                            else:
                                break
