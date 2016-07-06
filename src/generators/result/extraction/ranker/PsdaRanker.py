from generators.result import Logic


class PsdaRanker(Logic.Ranker):
    def __init__(self):
        Logic.Ranker.__init__(self)
        self.target_magnitude_handler = Logic.TargetMagnitude()
        self.sum_result_adder = Logic.SumResultAdder()

    def setup(self, options):
        Logic.Ranker.setup(self, options)
        self.target_magnitude_handler.setup(options)
        self.sum_result_adder.setup(options)

    def getResults(self, fft):
        result = self.target_magnitude_handler.getMagnitudesPerHarmonic(fft)
        return self.sum_result_adder.addSumAndOrderResult(result)

    # def getSNR(self, freq, harmonic_count, interpolation):
    #     result = 0
    #     for harmonic in range(harmonic_count):
    #         harmonic_freq = freq*(harmonic+1)
    #         result += interpolation(harmonic_freq)*2/(interpolation(harmonic_freq-1)+interpolation(harmonic_freq+1))
    #     return result
