import constants as c


class BruteForce(object):
    def __init__(self):
        self.windows = [c.WINDOW_NONE, c.WINDOW_HANNING, c.WINDOW_HAMMING, c.WINDOW_BLACKMAN, c.WINDOW_BARTLETT]
        self.interpolation = [c.INTERPOLATE_LINEAR, c.INTERPOLATE_NEAREST, c.INTERPOLATE_ZERO, c.INTERPOLATE_SLINEAR, c.INTERPOLATE_QUADRATIC, c.INTERPOLATE_CUBIC, c.INTERPOLATE_BARYCENTRIC]
        self.detrend = [c.LINEAR_DETREND, c.CONSTANT_DETREND, c.NONE_DETREND]
        self.length_range = tuple(32*2**i for i in range(5))
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


class DifferentialEvolution(object):
    def __init__(self):
        self.interpolation = [c.INTERPOLATE_NEAREST, c.INTERPOLATE_ZERO, c.INTERPOLATE_LINEAR, c.INTERPOLATE_SLINEAR, c.INTERPOLATE_QUADRATIC, c.INTERPOLATE_CUBIC, c.INTERPOLATE_BARYCENTRIC]
        self.length_range = tuple(128*2**i for i in range(2))
        self.step_range = tuple(32*2**i for i in range(3))
        self.break_range = tuple(i for i in range(0, 9, 2))
        self.bounds = (
            (0, 6.99),
            (0, 1.99),
            (0, 2.99),
            (0, 4.99),
            (0, 14),
        )

    def getBounds(self):
        return self.bounds

    def numbersToOptions(self, numbers):
        return {
            c.OPTIONS_WINDOW: c.WINDOW_KAISER,
            c.OPTIONS_INTERPOLATE: self.interpolation[int(numbers[0])],
            c.OPTIONS_DETREND: c.LINEAR_DETREND,
            c.OPTIONS_LENGTH: self.length_range[int(numbers[1])],
            c.OPTIONS_STEP: self.step_range[int(numbers[2])],
            c.OPTIONS_BREAK: self.break_range[int(numbers[3])],
            c.OPTIONS_FILTER: c.NONE_FILTER,
            c.OPTIONS_NORMALISE: 0,
            c.OPTIONS_ARG: numbers[4],
        }


class DifferentialEvolutionIdentification(object):
    def __init__(self):
        self.bounds = (
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 1),
            (0, 4),
            (0, 0.2),
            (0, 0.2),
            (0, 0.2),
            (0, 0.2),
            (0, 0.2),
            # (0, 5),
            # (0, 5),
            (0, 20),
            (0, 5),
        )

    def numbersToOptions(self, numbers):
        return {
            c.DATA_EXTRACTION_WEIGHTS: {
                1: {
                    1: numbers[0],
                    2: numbers[1],
                    3: numbers[2],
                    c.RESULT_SUM: numbers[3],
                },
                2: {
                    c.RESULT_SUM: numbers[4],
                }
            },
            c.DATA_EXTRACTION_DIFFERENCES: {
                1: {
                    1: numbers[5],
                    2: numbers[6],
                    3: numbers[7],
                    c.RESULT_SUM: numbers[8],
                },
                2: {
                    c.RESULT_SUM: numbers[9],
                }
            },
            # c.DATA_ACTUAL_RESULTS: {
            #     c.DATA_TARGET_THRESHOLD: numbers[10],
            #     c.DATA_WEIGHT_THRESHOLD: numbers[11],
            # },
            c.DATA_PREV_RESULTS: {
                c.DATA_TARGET_THRESHOLD: numbers[10],
                c.DATA_WEIGHT_THRESHOLD: numbers[11],
            }
        }

    def getBounds(self):
        return self.bounds
