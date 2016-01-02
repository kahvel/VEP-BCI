import numpy as np

import constants as c
import ListByTrials


class Results(ListByTrials.ListByTrials):
    def __init__(self):
        ListByTrials.ListByTrials.__init__(self)
        self.prev_result = None

    def start(self, target_freqs):
        ListByTrials.ListByTrials.start(self, target_freqs)
        self.prev_result = None

    def getTrialCollection(self, target_freqs):
        return {
            "Results": {current: {detected: 0 for detected in target_freqs} for current in target_freqs+[None]},
            "Targets": len(target_freqs),
            "TotalTime": 0,
            "TotalTimeSec": 0
        }

    def add(self, current, detected):
        self.current_data["Results"][current][detected] += 1
        self.prev_result = detected

    def trialtoString(self, trial):
        if len(trial) == 4:
            return "No results"
        result = "Total time: " + str(trial["TotalTime"]) + " Packets; " + str(trial["TotalTimeSec"]) + " sec"
        result += "\nTime per target: " + str(trial["TimePerTarget"])
        result += "\nAcc: " + str(trial["Accuracy"]) + " (Correct: " + str(trial["Correct"]) + " Wrong: " + str(trial["Wrong"]) + " Total: " + str(trial["Correct"]+trial["Wrong"]) + ")"
        result += "\nITR: " + str(trial["ITR"]) + " bit/trial; " + str(trial["ITRt"]) + " bits/min\n"
        for freq in trial["Results"]:
            result += str(freq) + " " + str(trial["Results"][freq]) + "\n"
        return result

    def trialEnded(self, total_time):
        self.current_data["TotalTime"] += total_time
        time_sec = self.getTimeInSec(total_time)
        self.current_data["TotalTimeSec"] += time_sec
        correct, wrong = self.getCorrectAndWrong(self.current_data)
        self.current_data["Correct"] = correct
        self.current_data["Wrong"] = wrong
        accuracy = self.getAccuracy(correct, wrong)
        self.current_data["Accuracy"] = accuracy
        target_count = self.current_data["Targets"]
        itr = self.getItr(accuracy, target_count)
        time_per_target = self.getTimePerTarget(correct+wrong, time_sec)
        self.current_data["TimePerTarget"] = time_per_target
        self.current_data["ITR"] = itr
        self.current_data["ITRt"] = self.getItrT(itr, time_per_target)
        ListByTrials.ListByTrials.trialEnded(self)

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

    def getCorrectAndWrong(self, trial):
        correct_results = 0
        wrong_results = 0
        for detected in trial["Results"]:
            for correct in trial["Results"][detected]:
                if detected == correct:
                    correct_results += trial["Results"][detected][correct]
                else:
                    wrong_results += trial["Results"][detected][correct]
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
        for i in range(len(self.list)):
            result += str(i) + "\n" + self.trialtoString(self.list[i])
        return result

    def isPrevResult(self, result):
        return result == self.prev_result
