__author__ = 'Anti'

import numpy as np
import constants as c


class Results(object):
    def __init__(self):
        self.results = {}
        self.prev_result = None
        self.trial_id = 0

    def reset(self):
        self.results = {}

    def setup(self, target_freqs):
        self.trial_id += 1
        self.results[self.trial_id] = {}
        self.results[self.trial_id]["Results"] = {current: {detected: 0 for detected in target_freqs} for current in target_freqs+[None]}
        self.results[self.trial_id]["Targets"] = len(target_freqs)

    def save(self):
        pass

    def addResult(self, current, detected):
        self.results[self.trial_id]["Results"][current][detected] += 1
        self.prev_result = detected

    def trialtoString(self, trial_id):
        res = self.results[trial_id]
        if len(res) == 2:
            return "No results"
        result = "Total time: " + str(res["TotalTime"]) + " Packets; " + str(res["TotalTimeSec"]) + " sec"
        result += "\nTime per target: " + str(res["TimePerTarget"])
        result += "\nAcc: " + str(res["Accuracy"]) + " (Correct: " + str(res["Correct"]) + " Wrong: " + str(res["Wrong"]) + " Total: " + str(res["Correct"]+res["Wrong"]) + ")"
        result += "\nITR: " + str(res["ITR"]) + " bit/trial; " + str(res["ITRt"]) + " bits/min\n"
        for freq in res["Results"]:
            result += str(freq) + " " + str(res["Results"][freq]) + "\n"
        return result

    def trialEnded(self, total_time):
        self.results[self.trial_id]["TotalTime"] = total_time
        time_sec = self.getTimeInSec(total_time)
        self.results[self.trial_id]["TotalTimeSec"] = time_sec
        correct, wrong = self.getCorrectAndWrong()
        self.results[self.trial_id]["Correct"] = correct
        self.results[self.trial_id]["Wrong"] = wrong
        accuracy = self.getAccuracy(correct, wrong)
        self.results[self.trial_id]["Accuracy"] = accuracy
        target_count = self.results[self.trial_id]["Targets"]
        itr = self.getItr(accuracy, target_count)
        time_per_target = self.getTimePerTarget(correct+wrong, time_sec)
        self.results[self.trial_id]["TimePerTarget"] = time_per_target
        self.results[self.trial_id]["ITR"] = itr
        self.results[self.trial_id]["ITRt"] = self.getItrT(itr, time_per_target)

    def getTimePerTarget(self, total_results, total_time):
        if total_results == 0:
            return np.nan
        else:
            return float(total_time)/total_results

    def getTimeInSec(self, time):
        return float(time)/c.HEADSET_FREQ

    def log2(self, x):
        if x == 0:
            return np.nan
        else:
            return np.log10(x)/np.log10(2)

    def getCorrectAndWrong(self):
        correct_results = 0
        wrong_results = 0
        for detected in self.results[self.trial_id]["Results"]:
            for correct in self.results[self.trial_id]["Results"][detected]:
                if detected == correct:
                    correct_results += self.results[self.trial_id]["Results"][detected][correct]
                else:
                    wrong_results += self.results[self.trial_id]["Results"][detected][correct]
        return correct_results, wrong_results

    def getAccuracy(self, correct, wrong):
        if correct+wrong == 0:
            return np.nan
        else:
            return float(correct)/(correct+wrong)

    def getItrT(self, itr, time):
        return itr*60.0/time

    def getItr(self, P, N):
        if N == 1:
            return np.nan
        elif P == 1:
            return self.log2(N)+P*self.log2(P)
        else:
            return self.log2(N)+P*self.log2(P)+(1-P)*self.log2((1-P)/(N-1))

    def __repr__(self):
        result = ""
        for trial in self.results:
            result += str(trial) + "\n" + self.trialtoString(trial)
        return result

    def isPrevResult(self, result):
        return result == self.prev_result
