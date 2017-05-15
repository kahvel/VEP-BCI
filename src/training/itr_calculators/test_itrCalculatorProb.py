from unittest import TestCase
from training.itr_calculators import ItrCalculatorProb

import numpy as np


class TestItrCalculatorProb(TestCase):
    def setUp(self):
        """
        Strukture: pi_cj = [
          [F_1|C_1, F_1|C_2, F_1|C_3],
          [F_2|C_1, F_2|C_2, F_2|C_3],
          [F_3|C_1, F_3|C_2, F_3|C_3]
        ]
        :return:
        """
        self.F1_C1 = 0.3
        self.F2_C1 = 0.4
        self.F3_C1 = 0.6
        self.F1_C2 = 0.4
        self.F2_C2 = 0.5
        self.F3_C2 = 0.3
        self.F1_C3 = 0.5
        self.F2_C3 = 0.1
        self.F3_C3 = 0.8

        self.f1_C1 = 0.2
        self.f2_C1 = 0.1
        self.f3_C1 = 0.666
        self.f1_C2 = 0.4
        self.f2_C2 = 0.12
        self.f3_C2 = 0.6
        self.f1_C3 = 0.6
        self.f2_C3 = 0.7
        self.f3_C3 = 0.9

        self.cdfs_pi_cj = [
          [self.F1_C1, self.F1_C2, self.F1_C3],
          [self.F2_C1, self.F2_C2, self.F2_C3],
          [self.F3_C1, self.F3_C2, self.F3_C3]
        ]
        self.pdfs_pi_cj = [
          [self.f1_C1, self.f1_C2, self.f1_C3],
          [self.f2_C1, self.f2_C2, self.f2_C3],
          [self.f3_C1, self.f3_C2, self.f3_C3]
        ]
        self.window_length=1
        self.step=0.125
        self.feature_maf_length=3
        self.proba_maf_length=3
        self.look_back_length=1
        self.n_targets=3,
        self.cdfs_cj_pi = np.transpose(self.cdfs_pi_cj)
        self.pdfs_cj_pi = np.transpose(self.pdfs_pi_cj)
        self.calculator = ItrCalculatorProb.ItrCalculatorProb(
            self.window_length,
            self.step,
            self.feature_maf_length,
            self.proba_maf_length,
            self.look_back_length,
            self.n_targets
        )
        self.class_probas = [1.0/len(self.cdfs_cj_pi) for _ in range(len(self.cdfs_cj_pi))]
        self.calculator.n_classes = len(self.cdfs_cj_pi)
        self.calculator.class_probas = self.class_probas

    def P1_C1(self):
        return (1-self.F1_C1)*(self.F2_C1)*(self.F3_C1)

    def P1_C2(self):
        return (1-self.F1_C2)*(self.F2_C2)*(self.F3_C2)

    def P1_C3(self):
        return (1-self.F1_C3)*(self.F2_C3)*(self.F3_C3)

    def P2_C1(self):
        return (self.F1_C1)*(1-self.F2_C1)*(self.F3_C1)

    def P2_C2(self):
        return (self.F1_C2)*(1-self.F2_C2)*(self.F3_C2)

    def P2_C3(self):
        return (self.F1_C3)*(1-self.F2_C3)*(self.F3_C3)

    def P3_C1(self):
        return (self.F1_C1)*(self.F2_C1)*(1-self.F3_C1)

    def P3_C2(self):
        return (self.F1_C2)*(self.F2_C2)*(1-self.F3_C2)

    def P3_C3(self):
        return (self.F1_C3)*(self.F2_C3)*(1-self.F3_C3)

    def P1_C1_d1(self):
        return (-self.f1_C1)*(self.F2_C1)*(self.F3_C1)

    def P1_C2_d1(self):
        return (-self.f1_C2)*(self.F2_C2)*(self.F3_C2)

    def P1_C3_d1(self):
        return (-self.f1_C3)*(self.F2_C3)*(self.F3_C3)

    def P2_C1_d1(self):
        return (self.f1_C1)*(1-self.F2_C1)*(self.F3_C1)

    def P2_C2_d1(self):
        return (self.f1_C2)*(1-self.F2_C2)*(self.F3_C2)

    def P2_C3_d1(self):
        return (self.f1_C3)*(1-self.F2_C3)*(self.F3_C3)

    def P3_C1_d1(self):
        return (self.f1_C1)*(self.F2_C1)*(1-self.F3_C1)

    def P3_C2_d1(self):
        return (self.f1_C2)*(self.F2_C2)*(1-self.F3_C2)

    def P3_C3_d1(self):
        return (self.f1_C3)*(self.F2_C3)*(1-self.F3_C3)

    def P1_C1_d2(self):
        return (1-self.F1_C1)*(self.f2_C1)*(self.F3_C1)

    def P1_C2_d2(self):
        return (1-self.F1_C2)*(self.f2_C2)*(self.F3_C2)

    def P1_C3_d2(self):
        return (1-self.F1_C3)*(self.f2_C3)*(self.F3_C3)

    def P2_C1_d2(self):
        return (self.F1_C1)*(-self.f2_C1)*(self.F3_C1)

    def P2_C2_d2(self):
        return (self.F1_C2)*(-self.f2_C2)*(self.F3_C2)

    def P2_C3_d2(self):
        return (self.F1_C3)*(-self.f2_C3)*(self.F3_C3)

    def P3_C1_d2(self):
        return (self.F1_C1)*(self.f2_C1)*(1-self.F3_C1)

    def P3_C2_d2(self):
        return (self.F1_C2)*(self.f2_C2)*(1-self.F3_C2)

    def P3_C3_d2(self):
        return (self.F1_C3)*(self.f2_C3)*(1-self.F3_C3)

    def P1_C1_d3(self):
        return (1-self.F1_C1)*(self.F2_C1)*(self.f3_C1)

    def P1_C2_d3(self):
        return (1-self.F1_C2)*(self.F2_C2)*(self.f3_C2)

    def P1_C3_d3(self):
        return (1-self.F1_C3)*(self.F2_C3)*(self.f3_C3)

    def P2_C1_d3(self):
        return (self.F1_C1)*(1-self.F2_C1)*(self.f3_C1)

    def P2_C2_d3(self):
        return (self.F1_C2)*(1-self.F2_C2)*(self.f3_C2)

    def P2_C3_d3(self):
        return (self.F1_C3)*(1-self.F2_C3)*(self.f3_C3)

    def P3_C1_d3(self):
        return (self.F1_C1)*(self.F2_C1)*(-self.f3_C1)

    def P3_C2_d3(self):
        return (self.F1_C2)*(self.F2_C2)*(-self.f3_C2)

    def P3_C3_d3(self):
        return (self.F1_C3)*(self.F2_C3)*(-self.f3_C3)

    def P1_C(self):
        return [
            self.P1_C1(),
            self.P1_C2(),
            self.P1_C3(),
        ]

    def P2_C(self):
        return [
            self.P2_C1(),
            self.P2_C2(),
            self.P2_C3(),
        ]

    def P3_C(self):
        return [
            self.P3_C1(),
            self.P3_C2(),
            self.P3_C3(),
        ]

    def P1_C_d1(self):
        return [
            self.P1_C1_d1(),
            self.P1_C2_d1(),
            self.P1_C3_d1(),
        ]

    def P1_C_d2(self):
        return [
            self.P1_C1_d2(),
            self.P1_C2_d2(),
            self.P1_C3_d2(),
        ]

    def P1_C_d3(self):
        return [
            self.P1_C1_d3(),
            self.P1_C2_d3(),
            self.P1_C3_d3(),
        ]

    def P2_C_d1(self):
        return [
            self.P2_C1_d1(),
            self.P2_C2_d1(),
            self.P2_C3_d1(),
        ]

    def P2_C_d2(self):
        return [
            self.P2_C1_d2(),
            self.P2_C2_d2(),
            self.P2_C3_d2(),
        ]

    def P2_C_d3(self):
        return [
            self.P2_C1_d3(),
            self.P2_C2_d3(),
            self.P2_C3_d3(),
        ]

    def P3_C_d1(self):
        return [
            self.P3_C1_d1(),
            self.P3_C2_d1(),
            self.P3_C3_d1(),
        ]

    def P3_C_d2(self):
        return [
            self.P3_C1_d2(),
            self.P3_C2_d2(),
            self.P3_C3_d2(),
        ]

    def P3_C_d3(self):
        return [
            self.P3_C1_d3(),
            self.P3_C2_d3(),
            self.P3_C3_d3(),
        ]

    def calculateR(self):
        return sum([
            sum([
                self.P1_C1()*self.class_probas[0],
                self.P1_C2()*self.class_probas[1],
                self.P1_C3()*self.class_probas[2]
            ]),sum([
                self.P2_C1()*self.class_probas[0],
                self.P2_C2()*self.class_probas[1],
                self.P2_C3()*self.class_probas[2]
            ]),sum([
                self.P3_C1()*self.class_probas[0],
                self.P3_C2()*self.class_probas[1],
                self.P3_C3()*self.class_probas[2]
            ])
        ])

    def calculateRderivative(self):
        return [
            sum([
                sum([
                    self.P1_C1_d1()*self.class_probas[0],
                    self.P1_C2_d1()*self.class_probas[1],
                    self.P1_C3_d1()*self.class_probas[2]
                ]),sum([
                    self.P2_C1_d1()*self.class_probas[0],
                    self.P2_C2_d1()*self.class_probas[1],
                    self.P2_C3_d1()*self.class_probas[2]
                ]),sum([
                    self.P3_C1_d1()*self.class_probas[0],
                    self.P3_C2_d1()*self.class_probas[1],
                    self.P3_C3_d1()*self.class_probas[2]
                ])
            ]),sum([
                sum([
                    self.P1_C1_d2()*self.class_probas[0],
                    self.P1_C2_d2()*self.class_probas[1],
                    self.P1_C3_d2()*self.class_probas[2]
                ]),sum([
                    self.P2_C1_d2()*self.class_probas[0],
                    self.P2_C2_d2()*self.class_probas[1],
                    self.P2_C3_d2()*self.class_probas[2]
                ]),sum([
                    self.P3_C1_d2()*self.class_probas[0],
                    self.P3_C2_d2()*self.class_probas[1],
                    self.P3_C3_d2()*self.class_probas[2]
                ])
            ]),sum([
                sum([
                    self.P1_C1_d3()*self.class_probas[0],
                    self.P1_C2_d3()*self.class_probas[1],
                    self.P1_C3_d3()*self.class_probas[2]
                ]),sum([
                    self.P2_C1_d3()*self.class_probas[0],
                    self.P2_C2_d3()*self.class_probas[1],
                    self.P2_C3_d3()*self.class_probas[2]
                ]),sum([
                    self.P3_C1_d3()*self.class_probas[0],
                    self.P3_C2_d3()*self.class_probas[1],
                    self.P3_C3_d3()*self.class_probas[2]
                ])
            ])
        ]

    def calculatePi(self, R):
        return [
            sum([
                self.P1_C1()*self.class_probas[0],
                self.P1_C2()*self.class_probas[1],
                self.P1_C3()*self.class_probas[2]
            ])/R,sum([
                self.P2_C1()*self.class_probas[0],
                self.P2_C2()*self.class_probas[1],
                self.P2_C3()*self.class_probas[2]
            ])/R,sum([
                self.P3_C1()*self.class_probas[0],
                self.P3_C2()*self.class_probas[1],
                self.P3_C3()*self.class_probas[2]
            ])/R
        ]

    def calculateLargePi(self):
        return [
            sum([
                self.P1_C1()*self.class_probas[0],
                self.P1_C2()*self.class_probas[1],
                self.P1_C3()*self.class_probas[2]
            ]),sum([
                self.P2_C1()*self.class_probas[0],
                self.P2_C2()*self.class_probas[1],
                self.P2_C3()*self.class_probas[2]
            ]),sum([
                self.P3_C1()*self.class_probas[0],
                self.P3_C2()*self.class_probas[1],
                self.P3_C3()*self.class_probas[2]
            ])
        ]

    def calculatePiDerivative(self, R, R_derivative):
        return [
            ([
                (sum([
                    self.P1_C1_d1()*self.class_probas[0],
                    self.P1_C2_d1()*self.class_probas[1],
                    self.P1_C3_d1()*self.class_probas[2]
                ])*R-R_derivative[0]*sum([
                    self.P1_C1()*self.class_probas[0],
                    self.P1_C2()*self.class_probas[1],
                    self.P1_C3()*self.class_probas[2]
                ]))/R**2,(sum([
                    self.P2_C1_d1()*self.class_probas[0],
                    self.P2_C2_d1()*self.class_probas[1],
                    self.P2_C3_d1()*self.class_probas[2]
                ])*R-R_derivative[0]*sum([
                    self.P2_C1()*self.class_probas[0],
                    self.P2_C2()*self.class_probas[1],
                    self.P2_C3()*self.class_probas[2]
                ]))/R**2,(sum([
                    self.P3_C1_d1()*self.class_probas[0],
                    self.P3_C2_d1()*self.class_probas[1],
                    self.P3_C3_d1()*self.class_probas[2]
                ])*R-R_derivative[0]*sum([
                    self.P3_C1()*self.class_probas[0],
                    self.P3_C2()*self.class_probas[1],
                    self.P3_C3()*self.class_probas[2]
                ]))/R**2
            ]),([
                (sum([
                    self.P1_C1_d2()*self.class_probas[0],
                    self.P1_C2_d2()*self.class_probas[1],
                    self.P1_C3_d2()*self.class_probas[2]
                ])*R-R_derivative[1]*sum([
                    self.P1_C1()*self.class_probas[0],
                    self.P1_C2()*self.class_probas[1],
                    self.P1_C3()*self.class_probas[2]
                ]))/R**2,(sum([
                    self.P2_C1_d2()*self.class_probas[0],
                    self.P2_C2_d2()*self.class_probas[1],
                    self.P2_C3_d2()*self.class_probas[2]
                ])*R-R_derivative[1]*sum([
                    self.P2_C1()*self.class_probas[0],
                    self.P2_C2()*self.class_probas[1],
                    self.P2_C3()*self.class_probas[2]
                ]))/R**2,(sum([
                    self.P3_C1_d2()*self.class_probas[0],
                    self.P3_C2_d2()*self.class_probas[1],
                    self.P3_C3_d2()*self.class_probas[2]
                ])*R-R_derivative[1]*sum([
                    self.P3_C1()*self.class_probas[0],
                    self.P3_C2()*self.class_probas[1],
                    self.P3_C3()*self.class_probas[2]
                ]))/R**2
            ]),([
                (sum([
                    self.P1_C1_d3()*self.class_probas[0],
                    self.P1_C2_d3()*self.class_probas[1],
                    self.P1_C3_d3()*self.class_probas[2]
                ])*R-R_derivative[2]*sum([
                    self.P1_C1()*self.class_probas[0],
                    self.P1_C2()*self.class_probas[1],
                    self.P1_C3()*self.class_probas[2]
                ]))/R**2,(sum([
                    self.P2_C1_d3()*self.class_probas[0],
                    self.P2_C2_d3()*self.class_probas[1],
                    self.P2_C3_d3()*self.class_probas[2]
                ])*R-R_derivative[2]*sum([
                    self.P2_C1()*self.class_probas[0],
                    self.P2_C2()*self.class_probas[1],
                    self.P2_C3()*self.class_probas[2]
                ]))/R**2,(sum([
                    self.P3_C1_d3()*self.class_probas[0],
                    self.P3_C2_d3()*self.class_probas[1],
                    self.P3_C3_d3()*self.class_probas[2]
                ])*R-R_derivative[2]*sum([
                    self.P3_C1()*self.class_probas[0],
                    self.P3_C2()*self.class_probas[1],
                    self.P3_C3()*self.class_probas[2]
                ]))/R**2
            ])
        ]

    def calculatePiGivenCjDerivative(self):
        return [
            [
                self.P1_C_d1(),
                self.P2_C_d1(),
                self.P3_C_d1()
            ],[
                self.P1_C_d2(),
                self.P2_C_d2(),
                self.P3_C_d2()
            ],[
                self.P1_C_d3(),
                self.P2_C_d3(),
                self.P3_C_d3()
            ]
        ]

    def calculateProbPiGivenCj(self):
        return [
            self.P1_C(),
            self.P2_C(),
            self.P3_C(),
        ]

    def calculateProbCk(self, R):
        return [
            sum([
                self.P1_C1()*self.class_probas[0],
                self.P2_C1()*self.class_probas[0],
                self.P3_C1()*self.class_probas[0],
            ])/R,sum([
                self.P1_C2()*self.class_probas[1],
                self.P2_C2()*self.class_probas[1],
                self.P3_C2()*self.class_probas[1],
            ])/R,sum([
                self.P1_C3()*self.class_probas[2],
                self.P2_C3()*self.class_probas[2],
                self.P3_C3()*self.class_probas[2]
            ])/R
        ]

    def calculateProbCkDerivative(self, R, R_derivative):
        return [
            ([
                (sum([
                    self.P1_C1_d1()*self.class_probas[0],
                    self.P2_C1_d1()*self.class_probas[0],
                    self.P3_C1_d1()*self.class_probas[0],
                ])*R-R_derivative[0]*sum([
                    self.P1_C1()*self.class_probas[0],
                    self.P2_C1()*self.class_probas[0],
                    self.P3_C1()*self.class_probas[0],
                ]))/R**2,(sum([
                    self.P1_C2_d1()*self.class_probas[1],
                    self.P2_C2_d1()*self.class_probas[1],
                    self.P3_C2_d1()*self.class_probas[1],
                ])*R-R_derivative[0]*sum([
                    self.P1_C2()*self.class_probas[1],
                    self.P2_C2()*self.class_probas[1],
                    self.P3_C2()*self.class_probas[1],
                ]))/R**2,(sum([
                    self.P1_C3_d1()*self.class_probas[2],
                    self.P2_C3_d1()*self.class_probas[2],
                    self.P3_C3_d1()*self.class_probas[2]
                ])*R-R_derivative[0]*sum([
                    self.P1_C3()*self.class_probas[2],
                    self.P2_C3()*self.class_probas[2],
                    self.P3_C3()*self.class_probas[2]
                ]))/R**2
            ]),([
                (sum([
                    self.P1_C1_d2()*self.class_probas[0],
                    self.P2_C1_d2()*self.class_probas[0],
                    self.P3_C1_d2()*self.class_probas[0],
                ])*R-R_derivative[1]*sum([
                    self.P1_C1()*self.class_probas[0],
                    self.P2_C1()*self.class_probas[0],
                    self.P3_C1()*self.class_probas[0],
                ]))/R**2,(sum([
                    self.P1_C2_d2()*self.class_probas[1],
                    self.P2_C2_d2()*self.class_probas[1],
                    self.P3_C2_d2()*self.class_probas[1],
                ])*R-R_derivative[1]*sum([
                    self.P1_C2()*self.class_probas[1],
                    self.P2_C2()*self.class_probas[1],
                    self.P3_C2()*self.class_probas[1],
                ]))/R**2,(sum([
                    self.P1_C3_d2()*self.class_probas[2],
                    self.P2_C3_d2()*self.class_probas[2],
                    self.P3_C3_d2()*self.class_probas[2]
                ])*R-R_derivative[1]*sum([
                    self.P1_C3()*self.class_probas[2],
                    self.P2_C3()*self.class_probas[2],
                    self.P3_C3()*self.class_probas[2]
                ]))/R**2
            ]),([
                (sum([
                    self.P1_C1_d3()*self.class_probas[0],
                    self.P2_C1_d3()*self.class_probas[0],
                    self.P3_C1_d3()*self.class_probas[0],
                ])*R-R_derivative[2]*sum([
                    self.P1_C1()*self.class_probas[0],
                    self.P2_C1()*self.class_probas[0],
                    self.P3_C1()*self.class_probas[0],
                ]))/R**2,(sum([
                    self.P1_C2_d3()*self.class_probas[1],
                    self.P2_C2_d3()*self.class_probas[1],
                    self.P3_C2_d3()*self.class_probas[1],
                ])*R-R_derivative[2]*sum([
                    self.P1_C2()*self.class_probas[1],
                    self.P2_C2()*self.class_probas[1],
                    self.P3_C2()*self.class_probas[1],
                ]))/R**2,(sum([
                    self.P1_C3_d3()*self.class_probas[2],
                    self.P2_C3_d3()*self.class_probas[2],
                    self.P3_C3_d3()*self.class_probas[2]
                ])*R-R_derivative[2]*sum([
                    self.P1_C3()*self.class_probas[2],
                    self.P2_C3()*self.class_probas[2],
                    self.P3_C3()*self.class_probas[2]
                ]))/R**2
            ])
        ]

    def test_transposeParameterMatrix(self):
        matrix = [
            [(1,2,3),(4,5,6)],
            [(1,1,1),(2,2,2)]
        ]
        transposed = [
            [(1,2,3),(1,1,1)],
            [(4,5,6),(2,2,2)]
        ]
        np.testing.assert_almost_equal(matrix, self.calculator.transposeParameterMatrix(transposed))

    def test_probPiGivenCj(self):
        actual = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        expected = self.calculateProbPiGivenCj()
        self.assertEqual(actual, expected)

    def test_probPiGivenCjDerivative(self):
        actual = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        expected = self.calculatePiGivenCjDerivative()
        np.testing.assert_almost_equal(actual, expected, 16)

    def test_probPiLarge(self):
        actual = self.calculator.probPiLarge(self.calculator.probPiGivenCj(self.cdfs_cj_pi))
        expected = self.calculateLargePi()
        self.assertEqual(actual, expected)

    def test_probPiLargeDerivative(self):
        actual = self.calculator.probPiLargeDerivative(self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi))
        expected = [
            [
                sum([
                    self.P1_C1_d1()*self.class_probas[0],
                    self.P1_C2_d1()*self.class_probas[1],
                    self.P1_C3_d1()*self.class_probas[2],
                ]),sum([
                    self.P2_C1_d1()*self.class_probas[0],
                    self.P2_C2_d1()*self.class_probas[1],
                    self.P2_C3_d1()*self.class_probas[2],
                ]),sum([
                    self.P3_C1_d1()*self.class_probas[0],
                    self.P3_C2_d1()*self.class_probas[1],
                    self.P3_C3_d1()*self.class_probas[2],
                ])
            ],[
                sum([
                    self.P1_C1_d2()*self.class_probas[0]+\
                    self.P1_C2_d2()*self.class_probas[1]+\
                    self.P1_C3_d2()*self.class_probas[2]
                ]),sum([
                    self.P2_C1_d2()*self.class_probas[0]+\
                    self.P2_C2_d2()*self.class_probas[1]+\
                    self.P2_C3_d2()*self.class_probas[2]
                ]),sum([
                    self.P3_C1_d2()*self.class_probas[0]+\
                    self.P3_C2_d2()*self.class_probas[1]+\
                    self.P3_C3_d2()*self.class_probas[2]
                ])
            ],[
                sum([
                    self.P1_C1_d3()*self.class_probas[0]+\
                    self.P1_C2_d3()*self.class_probas[1]+\
                    self.P1_C3_d3()*self.class_probas[2]
                ]),sum([
                    self.P2_C1_d3()*self.class_probas[0]+\
                    self.P2_C2_d3()*self.class_probas[1]+\
                    self.P2_C3_d3()*self.class_probas[2]
                ]),sum([
                    self.P3_C1_d3()*self.class_probas[0]+\
                    self.P3_C2_d3()*self.class_probas[1]+\
                    self.P3_C3_d3()*self.class_probas[2]
                ])
            ]
        ]
        np.testing.assert_almost_equal(actual, expected)
        # self.assertEqual(actual, expected)

    def test_probPi(self):
        pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        actual = self.calculator.probPi(self.calculator.probPiLarge(pi_given_cj), self.calculator.calculateR(self.calculator.probPiLarge(pi_given_cj)))
        R = self.calculateR()
        expected = self.calculatePi(R)
        self.assertEqual(actual, expected)

    def test_probCk(self):
        pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        actual = self.calculator.probCk(self.calculator.probCkLarge(pi_given_cj), self.calculator.calculateR(self.calculator.probPiLarge(pi_given_cj)))
        R = self.calculateR()
        expected = self.calculateProbCk(R)
        np.testing.assert_almost_equal(actual, expected, 16)

    def test_calculateR(self):
        actual = self.calculator.calculateR(self.calculator.probPiLarge(self.calculator.probPiGivenCj(self.cdfs_cj_pi)))
        expected = sum(self.calculateLargePi())
        self.assertEqual(actual, expected)

    def test_probPiDerivative(self):
        prob_pi_large = self.calculator.probPiLarge(self.calculator.probPiGivenCj(self.cdfs_cj_pi))
        prob_pi_large_derivative = self.calculator.probPiLargeDerivative(self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi))
        R = self.calculator.calculateR(prob_pi_large)
        R_derivative = self.calculator.rDerivative(prob_pi_large_derivative)
        actual = self.calculator.probPiDerivative(prob_pi_large, prob_pi_large_derivative, R, R_derivative)

        R = self.calculateR()
        R_derivative = self.calculateRderivative()
        expected = self.calculatePiDerivative(R, R_derivative)

        self.assertEqual(actual, expected)

    def test_probCkDerivative(self):
        prob_ck_large = self.calculator.probCkLarge(self.calculator.probPiGivenCj(self.cdfs_cj_pi))
        prob_pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        prob_ck_large_derivative = self.calculator.probCkLargeDerivative(prob_pi_given_cj_derivative)
        prob_pi_large_derivative = self.calculator.probPiLargeDerivative(prob_pi_given_cj_derivative)
        R = self.calculator.calculateR(prob_ck_large)
        R_derivative = self.calculator.rDerivative(prob_pi_large_derivative)
        actual = self.calculator.probCkDerivative(prob_ck_large, prob_ck_large_derivative, R, R_derivative)
        R = self.calculateR()
        R_derivative = self.calculateRderivative()
        expected = self.calculateProbCkDerivative(R, R_derivative)
        np.testing.assert_almost_equal(actual, expected, 16)

    def test_probCkLarge(self):
        pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        actual = self.calculator.probCkLarge(pi_given_cj)
        expected = [
            sum([
                self.P1_C1()*self.class_probas[0],
                self.P2_C1()*self.class_probas[0],
                self.P3_C1()*self.class_probas[0],
            ]),sum([
                self.P1_C2()*self.class_probas[1],
                self.P2_C2()*self.class_probas[1],
                self.P3_C2()*self.class_probas[1],
            ]),sum([
                self.P1_C3()*self.class_probas[2],
                self.P2_C3()*self.class_probas[2],
                self.P3_C3()*self.class_probas[2]
            ])
        ]
        np.testing.assert_almost_equal(actual, expected, 16)

    def test_probCkLargeDerivative(self):
        pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        actual = self.calculator.probCkLargeDerivative(pi_given_cj_derivative)
        expected = [
            ([
                sum([
                    self.P1_C1_d1()*self.class_probas[0],
                    self.P2_C1_d1()*self.class_probas[0],
                    self.P3_C1_d1()*self.class_probas[0],
                ]),sum([
                    self.P1_C2_d1()*self.class_probas[1],
                    self.P2_C2_d1()*self.class_probas[1],
                    self.P3_C2_d1()*self.class_probas[1],
                ]),sum([
                    self.P1_C3_d1()*self.class_probas[2],
                    self.P2_C3_d1()*self.class_probas[2],
                    self.P3_C3_d1()*self.class_probas[2]
                ])
            ]),([
                sum([
                    self.P1_C1_d2()*self.class_probas[0],
                    self.P2_C1_d2()*self.class_probas[0],
                    self.P3_C1_d2()*self.class_probas[0],
                ]),sum([
                    self.P1_C2_d2()*self.class_probas[1],
                    self.P2_C2_d2()*self.class_probas[1],
                    self.P3_C2_d2()*self.class_probas[1],
                ]),sum([
                    self.P1_C3_d2()*self.class_probas[2],
                    self.P2_C3_d2()*self.class_probas[2],
                    self.P3_C3_d2()*self.class_probas[2]
                ])
            ]),([
                sum([
                    self.P1_C1_d3()*self.class_probas[0],
                    self.P2_C1_d3()*self.class_probas[0],
                    self.P3_C1_d3()*self.class_probas[0],
                ]),sum([
                    self.P1_C2_d3()*self.class_probas[1],
                    self.P2_C2_d3()*self.class_probas[1],
                    self.P3_C2_d3()*self.class_probas[1],
                ]),sum([
                    self.P1_C3_d3()*self.class_probas[2],
                    self.P2_C3_d3()*self.class_probas[2],
                    self.P3_C3_d3()*self.class_probas[2]
                ])
            ])
        ]
        np.testing.assert_almost_equal(actual, expected, 16)

    def test_entropyP(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_large = self.calculator.probPiLarge(prob_pi_given_cj)
        R = self.calculator.calculateR(prob_pi_large)
        prob_pi = self.calculator.probPi(prob_pi_large, R)
        actual = self.calculator.entropyP(prob_pi)

        R = self.calculateR()
        pi = self.calculatePi(R)
        expected = -sum(map(lambda x: x*np.log2(x), pi))

        self.assertEqual(actual, expected)

    def test_entropyPderivative(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        prob_pi_large = self.calculator.probPiLarge(prob_pi_given_cj)
        prob_pi_large_derivative = self.calculator.probPiLargeDerivative(prob_pi_given_cj_derivative)
        R = self.calculator.calculateR(prob_pi_large)
        R_derivative = self.calculator.rDerivative(prob_pi_large_derivative)
        prob_pi = self.calculator.probPi(prob_pi_large, R)
        prob_pi_derivative = self.calculator.probPiDerivative(prob_pi_large, prob_pi_large_derivative, R, R_derivative)
        actual = self.calculator.entropyPderivative(prob_pi, prob_pi_derivative)
        R = self.calculateR()
        pi = self.calculatePi(R)
        pi_derivative = self.calculatePiDerivative(R, R_derivative)
        expected = [-sum(map(lambda (df, f): df*(np.log(f)+1)/np.log(2), zip(pi_d, pi))) for pi_d in pi_derivative]
        self.assertEqual(actual, expected)

    def test_entropyOfPgivenC(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        actual = self.calculator.entropyOfPgivenC(prob_pi_given_cj)

        pi_given_cj = self.calculateProbPiGivenCj()
        expected = -sum(map(lambda x: x*np.log2(x), pi_given_cj))
        np.testing.assert_almost_equal(actual, expected, 16)

    def test_entropyOfPgivenCderivative(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        actual = self.calculator.entropyOfPgivenCderivative(prob_pi_given_cj, prob_pi_given_cj_derivative)
        pi_given_cj = self.calculateProbPiGivenCj()
        pi_given_cj_derivative = self.calculatePiGivenCjDerivative()
        expected = [-sum(map(lambda (df, f): df*(np.log(f)+1)/np.log(2), zip(pi_d, pi_given_cj))) for pi_d in pi_given_cj_derivative]
        np.testing.assert_almost_equal(actual, expected, 16)

    def test_entropyPgivenC(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_large = self.calculator.probPiLarge(prob_pi_given_cj)
        R = self.calculator.calculateR(prob_pi_large)
        prob_ck_large = self.calculator.probCkLarge(prob_pi_given_cj)
        prob_ck = self.calculator.probCk(prob_ck_large, R)
        actual = self.calculator.entropyPgivenC(prob_ck, self.calculator.entropyOfPgivenC(prob_pi_given_cj))

        R = self.calculateR()
        pi_given_cj = self.calculateProbPiGivenCj()
        entropy_of_p_given_c = -sum(map(lambda x: x*np.log2(x), pi_given_cj))
        prob_ck = self.calculateProbCk(R)
        expected = sum(ck*entropy for ck, entropy in zip(prob_ck, entropy_of_p_given_c))
        np.testing.assert_almost_equal(actual, expected, 16)

    def test_entropyPgivenCderivative(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        prob_pi_large = self.calculator.probPiLarge(prob_pi_given_cj)
        prob_pi_large_derivative = self.calculator.probPiLargeDerivative(prob_pi_given_cj_derivative)
        R = self.calculator.calculateR(prob_pi_large)
        R_derivative = self.calculator.rDerivative(prob_pi_large_derivative)
        prob_ck_large = self.calculator.probCkLarge(prob_pi_given_cj)
        prob_ck_large_derivative = self.calculator.probCkLargeDerivative(prob_pi_given_cj_derivative)
        prob_ck = self.calculator.probCk(prob_ck_large, R)
        prob_ck_derivative = self.calculator.probCkDerivative(prob_ck_large, prob_ck_large_derivative, R, R_derivative)
        entropy_of_p_given_c_derivative = self.calculator.entropyOfPgivenCderivative(prob_pi_given_cj, prob_pi_given_cj_derivative)
        actual = self.calculator.entropyPgivenCderivative(prob_ck_derivative, self.calculator.entropyOfPgivenC(prob_pi_given_cj), prob_ck, entropy_of_p_given_c_derivative)

        R = self.calculateR()
        pi_given_cj_derivative = self.calculatePiGivenCjDerivative()
        pi_given_cj = self.calculateProbPiGivenCj()
        entropy_of_p_given_c = -sum(map(lambda x: x*np.log2(x), pi_given_cj))
        entropy_of_p_given_c_derivative = [-sum(map(lambda (df, f): df*(np.log(f)+1)/np.log(2), zip(pi_d, pi_given_cj))) for pi_d in pi_given_cj_derivative]
        prob_ck = self.calculateProbCk(R)
        prob_ck_derivative = self.calculateProbCkDerivative(R, R_derivative)
        expected = [sum(dc*entropy+de*ck for ck, entropy, de, dc in zip(prob_ck, entropy_of_p_given_c, d_entropy, d_ck)) for d_entropy, d_ck in zip(entropy_of_p_given_c_derivative, prob_ck_derivative)]
        np.testing.assert_almost_equal(actual, expected, 15)

    def test_mutualInformationDerivative(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        prob_pi_large = self.calculator.probPiLarge(prob_pi_given_cj)
        prob_pi_large_derivative = self.calculator.probPiLargeDerivative(prob_pi_given_cj_derivative)
        R = self.calculator.calculateR(prob_pi_large)
        R_derivative = self.calculator.rDerivative(prob_pi_large_derivative)
        prob_ck_large = self.calculator.probCkLarge(prob_pi_given_cj)
        prob_ck_large_derivative = self.calculator.probCkLargeDerivative(prob_pi_given_cj_derivative)
        prob_ck = self.calculator.probCk(prob_ck_large, R)
        prob_ck_derivative = self.calculator.probCkDerivative(prob_ck_large, prob_ck_large_derivative, R, R_derivative)
        entropy_of_p_given_c_derivative = self.calculator.entropyOfPgivenCderivative(prob_pi_given_cj, prob_pi_given_cj_derivative)
        actual_entropy_p_given_c_derivative = self.calculator.entropyPgivenCderivative(prob_ck_derivative, self.calculator.entropyOfPgivenC(prob_pi_given_cj), prob_ck, entropy_of_p_given_c_derivative)

        R = self.calculateR()
        pi_given_cj_derivative = self.calculatePiGivenCjDerivative()
        pi_given_cj = self.calculateProbPiGivenCj()
        entropy_of_p_given_c = -sum(map(lambda x: x*np.log2(x), pi_given_cj))
        entropy_of_p_given_c_derivative = [-sum(map(lambda (df, f): df*(np.log(f)+1)/np.log(2), zip(pi_d, pi_given_cj))) for pi_d in pi_given_cj_derivative]
        prob_ck = self.calculateProbCk(R)
        prob_ck_derivative = self.calculateProbCkDerivative(R, R_derivative)
        expected_entropy_p_given_c_derivative = [sum(dc*entropy+de*ck for ck, entropy, de, dc in zip(prob_ck, entropy_of_p_given_c, d_entropy, d_ck)) for d_entropy, d_ck in zip(entropy_of_p_given_c_derivative, prob_ck_derivative)]

        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        prob_pi_large = self.calculator.probPiLarge(prob_pi_given_cj)
        prob_pi_large_derivative = self.calculator.probPiLargeDerivative(prob_pi_given_cj_derivative)
        R = self.calculator.calculateR(prob_pi_large)
        R_derivative = self.calculator.rDerivative(prob_pi_large_derivative)
        prob_pi = self.calculator.probPi(prob_pi_large, R)
        prob_pi_derivative = self.calculator.probPiDerivative(prob_pi_large, prob_pi_large_derivative, R, R_derivative)
        actual_entropy_p_derivative = self.calculator.entropyPderivative(prob_pi, prob_pi_derivative)

        R = self.calculateR()
        pi = self.calculatePi(R)
        pi_derivative = self.calculatePiDerivative(R, R_derivative)
        expectedentropy_p_derivative = [-sum(map(lambda (df, f): df*(np.log(f)+1)/np.log(2), zip(pi_d, pi))) for pi_d in pi_derivative]

        actual = self.calculator.mutualInformationDerivative(actual_entropy_p_derivative, actual_entropy_p_given_c_derivative)
        expected = [a-b for a,b in zip(expectedentropy_p_derivative, expected_entropy_p_given_c_derivative)]

        np.testing.assert_almost_equal(actual, expected, 16)

    def test_mutualInformation(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_large = self.calculator.probPiLarge(prob_pi_given_cj)
        R = self.calculator.calculateR(prob_pi_large)
        prob_pi = self.calculator.probPi(prob_pi_large, R)
        entropyP = self.calculator.entropyP(prob_pi)
        prob_ck_large = self.calculator.probCkLarge(prob_pi_given_cj)
        prob_ck = self.calculator.probCk(prob_ck_large, R)
        entropy_of_p_given_c = self.calculator.entropyOfPgivenC(prob_pi_given_cj)
        entropyPgivenC = self.calculator.entropyPgivenC(prob_ck, entropy_of_p_given_c)
        actual = self.calculator.mutualInformation(entropyP, entropyPgivenC)

        pi_given_cj = self.calculateProbPiGivenCj()
        R = self.calculateR()
        pi = self.calculatePi(R)
        entropyP = -sum(map(lambda x: x*np.log2(x), pi))
        entropy_of_p_given_c = -sum(map(lambda x: x*np.log2(x), pi_given_cj))
        prob_ck = self.calculateProbCk(R)
        entropyPgivenC = sum(ck*entropy for ck, entropy in zip(prob_ck, entropy_of_p_given_c))
        expected = entropyP - entropyPgivenC
        np.testing.assert_almost_equal(actual, expected, 16)

    def test_rDerivative(self):
        pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        # R = self.calculator.calculateR(self.calculator.probPiLarge(pi_given_cj))
        # R_derivative = self.calculator
        actual = self.calculator.rDerivative(self.calculator.probPiLargeDerivative(pi_given_cj_derivative))
        expected = [
            sum([
                sum([
                    self.P1_C1_d1()*self.class_probas[0],
                    self.P1_C2_d1()*self.class_probas[1],
                    self.P1_C3_d1()*self.class_probas[2]
                ]),sum([
                    self.P2_C1_d1()*self.class_probas[0],
                    self.P2_C2_d1()*self.class_probas[1],
                    self.P2_C3_d1()*self.class_probas[2]
                ]),sum([
                    self.P3_C1_d1()*self.class_probas[0],
                    self.P3_C2_d1()*self.class_probas[1],
                    self.P3_C3_d1()*self.class_probas[2]
                ])
            ]),sum([
                sum([
                    self.P1_C1_d2()*self.class_probas[0],
                    self.P1_C2_d2()*self.class_probas[1],
                    self.P1_C3_d2()*self.class_probas[2]
                ]),sum([
                    self.P2_C1_d2()*self.class_probas[0],
                    self.P2_C2_d2()*self.class_probas[1],
                    self.P2_C3_d2()*self.class_probas[2]
                ]),sum([
                    self.P3_C1_d2()*self.class_probas[0],
                    self.P3_C2_d2()*self.class_probas[1],
                    self.P3_C3_d2()*self.class_probas[2]
                ])
            ]),sum([
                sum([
                    self.P1_C1_d3()*self.class_probas[0],
                    self.P1_C2_d3()*self.class_probas[1],
                    self.P1_C3_d3()*self.class_probas[2]
                ]),sum([
                    self.P2_C1_d3()*self.class_probas[0],
                    self.P2_C2_d3()*self.class_probas[1],
                    self.P2_C3_d3()*self.class_probas[2]
                ]),sum([
                    self.P3_C1_d3()*self.class_probas[0],
                    self.P3_C2_d3()*self.class_probas[1],
                    self.P3_C3_d3()*self.class_probas[2]
                ])
            ])
        ]
        self.assertEqual(actual, expected)

    def test_itrDerivative(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        prob_pi_large = self.calculator.probPiLarge(prob_pi_given_cj)
        prob_pi_large_derivative = self.calculator.probPiLargeDerivative(prob_pi_given_cj_derivative)
        R = self.calculator.calculateR(prob_pi_large)
        R_derivative = self.calculator.rDerivative(prob_pi_large_derivative)
        prob_pi = self.calculator.probPi(prob_pi_large, R)
        prob_pi_derivative = self.calculator.probPiDerivative(prob_pi_large, prob_pi_large_derivative, R, R_derivative)
        prob_ck_large = self.calculator.probCkLarge(prob_pi_given_cj)
        prob_ck_large_derivative = self.calculator.probCkLargeDerivative(prob_pi_given_cj_derivative)
        prob_ck = self.calculator.probCk(prob_ck_large, R)
        prob_ck_derivative = self.calculator.probCkDerivative(prob_ck_large, prob_ck_large_derivative, R, R_derivative)
        entropy_p = self.calculator.entropyP(prob_pi)
        entropy_p_derivative = self.calculator.entropyPderivative(prob_pi, prob_pi_derivative)
        entropy_of_p_given_c = self.calculator.entropyOfPgivenC(prob_pi_given_cj)
        entropy_of_p_given_c_derivative = self.calculator.entropyOfPgivenCderivative(prob_pi_given_cj, prob_pi_given_cj_derivative)
        entropy_p_given_c = self.calculator.entropyPgivenC(prob_ck, entropy_of_p_given_c)
        entropy_p_given_c_derivative = self.calculator.entropyPgivenCderivative(prob_ck_derivative, entropy_of_p_given_c, prob_ck, entropy_of_p_given_c_derivative)
        mutual_information = self.calculator.mutualInformation(entropy_p, entropy_p_given_c)
        mutual_information_derivative = self.calculator.mutualInformationDerivative(entropy_p_derivative, entropy_p_given_c_derivative)
        mdt = self.calculator.mdt(R)
        mdt_derivative = self.calculator.mdtDerivative(R, R_derivative)
        actual = self.calculator.itrDerivative(mutual_information, mutual_information_derivative, mdt, mdt_derivative)

        R_derivative = self.calculateRderivative()
        expected_mdt_derivative = [-self.step/R**2*dr for dr in R_derivative]
        expected_mdt = self.window_length + (self.feature_maf_length+self.proba_maf_length+self.look_back_length+1.0/R-4)*self.step

        R = self.calculateR()
        pi_given_cj_derivative = self.calculatePiGivenCjDerivative()
        pi_given_cj = self.calculateProbPiGivenCj()
        entropy_of_p_given_c = -sum(map(lambda x: x*np.log2(x), pi_given_cj))
        entropy_of_p_given_c_derivative = [-sum(map(lambda (df, f): df*(np.log(f)+1)/np.log(2), zip(pi_d, pi_given_cj))) for pi_d in pi_given_cj_derivative]
        prob_ck = self.calculateProbCk(R)
        prob_ck_derivative = self.calculateProbCkDerivative(R, R_derivative)
        expected_entropy_p_given_c_derivative = [sum(dc*entropy+de*ck for ck, entropy, de, dc in zip(prob_ck, entropy_of_p_given_c, d_entropy, d_ck)) for d_entropy, d_ck in zip(entropy_of_p_given_c_derivative, prob_ck_derivative)]

        R = self.calculateR()
        pi = self.calculatePi(R)
        pi_derivative = self.calculatePiDerivative(R, R_derivative)
        expectedentropy_p_derivative = [-sum(map(lambda (df, f): df*(np.log(f)+1)/np.log(2), zip(pi_d, pi))) for pi_d in pi_derivative]

        pi_given_cj = self.calculateProbPiGivenCj()
        R = self.calculateR()
        pi = self.calculatePi(R)
        entropyP = -sum(map(lambda x: x*np.log2(x), pi))
        entropy_of_p_given_c = -sum(map(lambda x: x*np.log2(x), pi_given_cj))
        prob_ck = self.calculateProbCk(R)
        entropyPgivenC = sum(ck*entropy for ck, entropy in zip(prob_ck, entropy_of_p_given_c))
        expected_mi = entropyP - entropyPgivenC
        expected_mi_derivative = [a-b for a,b in zip(expectedentropy_p_derivative, expected_entropy_p_given_c_derivative)]

        expected = [(ditr*mdt-dmdt*expected_mi)/expected_mdt**2*60 for ditr, dmdt in zip(expected_mi_derivative, expected_mdt_derivative)]

        np.testing.assert_almost_equal(actual, expected, 14)

    def test_mdtDerivative(self):
        prob_pi_given_cj = self.calculator.probPiGivenCj(self.cdfs_cj_pi)
        prob_pi_given_cj_derivative = self.calculator.probPiGivenCjDerivative(self.pdfs_cj_pi, self.cdfs_cj_pi)
        prob_pi_large = self.calculator.probPiLarge(prob_pi_given_cj)
        prob_pi_large_derivative = self.calculator.probPiLargeDerivative(prob_pi_given_cj_derivative)
        R = self.calculator.calculateR(prob_pi_large)
        R_derivative = self.calculator.rDerivative(prob_pi_large_derivative)
        actual = self.calculator.mdtDerivative(R, R_derivative)

        R = self.calculateR()
        R_derivative = self.calculateRderivative()
        expected = [-self.step/R**2*dr for dr in R_derivative]
        np.testing.assert_almost_equal(actual, expected, 16)

    # def test_product(self):
    #     self.fail()
    #
    # def test_pdf(self):
    #     self.fail()
    #
    # def test_cdf(self):
    #     self.fail()
    #
    # def test_fitCurves(self):
    #     self.fail()
    #
    # def test_calculateCurves(self):
    #     self.fail()
    #
    # def test_itrFromThresholds(self):
    #     self.fail()
    #
    # def test_itr(self):
    #     self.fail()

    # def test_allPdfs(self):
    #     self.fail()
    #
    # def test_allCdfs(self):
    #     self.fail()
    #
    # def test_gradient(self):
    #     self.fail()
