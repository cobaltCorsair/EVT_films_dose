import unittest
import logicStats
import numpy as np

class MyTestCase(unittest.TestCase):
    def test_something(self):
        # introducing loc variable for np.random.normal (mu variable in our notation)
        loc = 5.0
        # randomizing data
        data = np.random.normal(size=10000, loc=loc, scale=1.)
        # fitting the function and obtaining it's error
        gs, err = logicStats.prepareGauss(data)
        # checking whether obtained value of mu at gs[1] is within 3 sigma (err[1]) from original loc
        self.assertTrue(gs[1] - 3*err[1] <= loc <= gs[1] + 3*err[1])

    def test_funcCall(self):
        loc = 0.0
        data = np.random.normal(size=10000, loc=loc, scale=1.)
        gs, err = logicStats.prepareGauss(data)

        dte = logicStats.gauss(0.0, *gs)
        self.assertTrue(gs[0] - 3*err[0] <= dte <= gs[0] + 3*err[0])


if __name__ == '__main__':
    unittest.main()
