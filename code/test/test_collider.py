import unittest
"""
This file tests the functionality of the collider.py module. 
"""

import sys
sys.path.extend(['.', '..', '../external/', 'external/'])
import collider

from test_shared import *
import test_shared 
import time
from Residues import Residues

def get_non_UIS_from_transitions_old(transitions, collisions, par, MAX_UIS, unsorted=False):
    """ Get all combinations that are not UIS """
    #collisions
    #q3, q1, srm_id, peptide_key
    #transitions
    #q3, srm_id
    collisions_per_peptide = {}
    non_uis_list = [set() for i in range(MAX_UIS+1)]
    q3_window_used = par.q3_window
    for t in transitions:
        if par.ppm: q3_window_used = par.q3_window * 10**(-6) * t[0]
        this_min = q3_window_used
        for c in collisions:
            if abs( t[0] - c[0] ) <= q3_window_used:
                #gets all collisions
                if collisions_per_peptide.has_key(c[3]):
                    if not t[1] in collisions_per_peptide[c[3]]:
                        collisions_per_peptide[c[3]].append( t[1] )
                else: collisions_per_peptide[c[3]] = [ t[1] ] 
    #here we calculate the UIS for this peptide with the given RT-range
    for pepc in collisions_per_peptide.values():
        for i in range(1,MAX_UIS+1):
            collider.get_non_uis(pepc, non_uis_list[i], i)
    return non_uis_list

class Test_collider_function(unittest.TestCase): 

    def setUp(self):
        self.transitions = transitions_def1
        self.collisions  = collisions_def1
        class Minimal: pass
        self.par = Minimal()
        self.par.q3_window = 4.0
        self.par.ppm = False
        self.MAX_UIS = 5
        self.q3_high = 1500
        self.q3_low = 300

        self.par.bions      = True
        self.par.yions      = True
        self.par.aions      = False
        self.par.aMinusNH3  = False
        self.par.bMinusH2O  = False
        self.par.bMinusNH3  = False
        self.par.bPlusH2O   = False
        self.par.yMinusH2O  = False
        self.par.yMinusNH3  = False
        self.par.cions      = False
        self.par.xions      = False
        self.par.zions      = False
        self.par.MMinusH2O      = False
        self.par.MMinusNH3      = False


        def returnrange(): return self.q3_high, self.q3_low
        self.par.get_q3range_collisions = returnrange

        import sys
        self.R = Residues('mono')

        self.acollider = collider.SRMcollider()
        self.aparamset = collider.testcase()

    def test_getMinNeededTransitions_1(self):
        pep = test_shared.runpep1
        transitions = test_shared.runtransitions1
        precursors = test_shared.runprecursors1
        transitions = tuple([ (t[0], i) for i,t in enumerate(transitions)])
        par = self.par
        q3_high = self.q3_high
        q3_low = self.q3_low
        R = self.R
        par.max_uis = 15

        collisions = list(collider.SRMcollider._get_all_collisions_calculate_sub(
                collider.SRMcollider(), precursors, par, R, q3_low, q3_high))
        m = self.acollider._getMinNeededTransitions(par, transitions, collisions)
        self.assertEqual(m, 8)

        #now also test with lower q3 window
        par.q3_window = 1.0
        collisions = list(collider.SRMcollider._get_all_collisions_calculate_sub(
                collider.SRMcollider(), precursors, par, R, q3_low, q3_high))
        m = self.acollider._getMinNeededTransitions(par, transitions, collisions)
        self.assertEqual(m, 4)

    def test_getMinNeededTransitions_2(self):
        pep = test_shared.runpep2
        transitions = test_shared.runtransitions2
        precursors = test_shared.runprecursors2
        transitions = tuple([ (t[0], i) for i,t in enumerate(transitions)])
        par = self.par
        q3_high = self.q3_high
        q3_low = self.q3_low
        R = self.R
        par.max_uis = len(transitions) +  1

        collisions = list(collider.SRMcollider._get_all_collisions_calculate_sub(
                collider.SRMcollider(), precursors, par, R, q3_low, q3_high))
        m = self.acollider._getMinNeededTransitions(par, transitions, collisions)
        self.assertEqual(m, -1)

        #now also test with lower q3 window
        par.q3_window = 1.0
        collisions = list(collider.SRMcollider._get_all_collisions_calculate_sub(
                collider.SRMcollider(), precursors, par, R, q3_low, q3_high))
        m = self.acollider._getMinNeededTransitions(par, transitions, collisions)
        self.assertEqual(m, 6)

    def test_getMinNeededTransitions_unit(self):
        par = self.par
        par.max_uis = 5
        transitions = self.transitions
        collisions = self.collisions
        m = self.acollider._getMinNeededTransitions(par, transitions, collisions)
        self.assertEqual(m, -1)

        par.max_uis = 10 
        transitions = transitions_def3
        collisions = collisions_def3
        m = self.acollider._getMinNeededTransitions(par, transitions, collisions)
        self.assertEqual(m, -1)

        transitions = transitions_def4
        collisions = collisions_def4
        m = self.acollider._getMinNeededTransitions(par, transitions, collisions)
        self.assertEqual(m, 4)

        transitions = transitions_def5
        collisions = collisions_def5
        m = self.acollider._getMinNeededTransitions(par, transitions, collisions)
        self.assertEqual(m, 4)

    def test_get_non_uis(self):
        test = set()
        collider.get_non_uis( [1,2,3], test,2 )
        self.assertEqual(test, set([(1, 2), (1, 3), (2, 3)]) )
        test = set()
        collider.get_non_uis( [1,2,3,4], test,2 )
        self.assertEqual(test, set([(1, 2), (1, 3), (1, 4), (2, 3), (3, 4), (2, 4)]))

    def test_get_non_UIS_from_transitions1(self): 
        oldnon_uis = get_non_UIS_from_transitions_old(self.transitions, self.collisions, 
                                         self.par, self.MAX_UIS)
        self.assertEqual([len(l) for l in oldnon_uis[1:]], test_shared.lennonuis1)
        self.assertEqual(oldnon_uis, test_shared.refnonuis1)

    def test_get_non_UIS_from_transitions2(self): 
        self.transitions = test_shared.transitions_def2
        self.collisions  = test_shared.collisions_def2
        oldnon_uis = get_non_UIS_from_transitions_old(self.transitions,
            self.collisions, self.par, self.MAX_UIS)
        self.assertEqual([len(l) for l in oldnon_uis[1:]], test_shared.lennonuis2)
        self.assertEqual(oldnon_uis, test_shared.refnonuis2_sorted)

    def test_get_non_UIS_from_transitions3(self): 
        self.transitions = transitions_def3
        self.collisions  = collisions_def3
        oldnon_uis = get_non_UIS_from_transitions_old(self.transitions,
            self.collisions, self.par, self.MAX_UIS)
        self.assertEqual([len(l) for l in oldnon_uis[1:]], test_shared.lennonuis3)
        self.assertEqual(oldnon_uis, test_shared.refnonuis3)

    def test_get_non_UIS_from_transitions4(self): 
        self.transitions = transitions_def4
        self.collisions  = collisions_def4
        oldnon_uis = get_non_UIS_from_transitions_old(self.transitions,
            self.collisions, self.par, self.MAX_UIS)
        self.assertEqual([len(l) for l in oldnon_uis[1:]], test_shared.lennonuis4)
        self.assertEqual(oldnon_uis, test_shared.refnonuis4)

    def test_get_uis(self):
        non_uis_list = get_non_UIS_from_transitions_old(self.transitions,
                 self.collisions, self.par, self.MAX_UIS)
        srm_ids = [t[1] for t in self.transitions]
        rr = collider.get_uis(srm_ids, non_uis_list[2], 2)
        self.assertEqual(len(rr), 0)
        #
        self.transitions = transitions_def2
        self.collisions  = collisions_def2
        non_uis_list = get_non_UIS_from_transitions_old(self.transitions,
                 self.collisions, self.par, self.MAX_UIS)
        srm_ids = [t[1] for t in self.transitions]
        rr = collider.get_uis(srm_ids, non_uis_list[2], 2)
        self.assertEqual(len(rr), 1)

    def test_calculate_collisions_1(self):
        pep = test_shared.runpep1
        transitions = test_shared.runtransitions1
        precursors = test_shared.runprecursors1
        transitions = tuple([ (t[0], i) for i,t in enumerate(transitions)])
        par = self.par
        q3_high = self.q3_high
        q3_low = self.q3_low
        R = self.R

        collisions = list(collider.SRMcollider._get_all_collisions_calculate_sub(
                collider.SRMcollider(), precursors, par, R, q3_low, q3_high))
        collisions_per_peptide = {}
        q3_window_used = par.q3_window
        for t in transitions:
            if par.ppm: q3_window_used = par.q3_window * 10**(-6) * t[0]
            for c in collisions:
                if abs( t[0] - c[0] ) <= q3_window_used:
                    #gets all collisions
                    if collisions_per_peptide.has_key(c[3]):
                        if not t[1] in collisions_per_peptide[c[3]]:
                            collisions_per_peptide[c[3]].append( t[1] )
                    else: 
                        collisions_per_peptide[c[3]] = [ t[1] ] ; 

        self.assertEqual(collisions_per_peptide, test_shared.collpepresult1)

    def test_calculate_collisions_2(self):
        pep = test_shared.runpep2
        transitions = test_shared.runtransitions2
        precursors = test_shared.runprecursors2
        transitions = tuple([ (t[0], i) for i,t in enumerate(transitions)])
        par = self.par
        q3_high = self.q3_high
        q3_low = self.q3_low
        R = self.R

        collisions = list(collider.SRMcollider._get_all_collisions_calculate_sub(
                collider.SRMcollider(), precursors, par, R, q3_low, q3_high))
        collisions_per_peptide = {}
        q3_window_used = par.q3_window
        for t in transitions:
            if par.ppm: q3_window_used = par.q3_window * 10**(-6) * t[0]
            for c in collisions:
                if abs( t[0] - c[0] ) <= q3_window_used:
                    #gets all collisions
                    if collisions_per_peptide.has_key(c[3]):
                        if not t[1] in collisions_per_peptide[c[3]]:
                            collisions_per_peptide[c[3]].append( t[1] )
                    else: 
                        collisions_per_peptide[c[3]] = [ t[1] ] ; 

        self.assertEqual(collisions_per_peptide, test_shared.collpepresult2)

    def test_get_uis_extra1(self):

        order =  1
        nonuis = set([(1627247L,), (1627240L,), (1627241L,), (1627242L,), (1627248L,), (1627243L,), (1627238L,), (1627249L,), (1627244L,), (1627239L,), (1627250L,), (1627251L,), (1627252L,)])
        srm_ids = [1627238L, 1627239L, 1627240L, 1627241L, 1627242L, 1627243L, 1627244L, 1627247L, 1627248L, 1627249L, 1627250L, 1627251L, 1627252L]
        uis_list = collider.get_uis(srm_ids, nonuis, order)
        self.assertEqual( len(uis_list), 0)

    def test_choose(self): 
        self.assertEqual(10,  collider.choose( 5,2) )
        self.assertEqual(10,  collider.choose( 5,3) )
        self.assertEqual(45,  collider.choose(10,2) )
        self.assertEqual(120, collider.choose(10,3) )
        self.assertEqual(210, collider.choose(10,4) )

    def test_combinations(self):
        comb52 = list(collider.combinations( range(5), 2 ) )
        self.assertEqual(comb52, [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 3),
            (2, 4),
            (3, 4)
        ])
        comb53 = list(collider.combinations( range(5), 3 ) )
        self.assertEqual( comb53, [
            (0, 1, 2),
            (0, 1, 3),
            (0, 1, 4),
            (0, 2, 3), 
            (0, 2, 4),
            (0, 3, 4),
            (1, 2, 3),
            (1, 2, 4),
            (1, 3, 4),
            (2, 3, 4)
        ])

        # now also test the before 2.6 version

        comb52 = list(collider.combinations( range(5), 2, True ) )
        self.assertEqual(comb52, [
            (0, 1),
            (0, 2),
            (0, 3),
            (0, 4),
            (1, 2),
            (1, 3),
            (1, 4),
            (2, 3),
            (2, 4),
            (3, 4)
        ])
        comb53 = list(collider.combinations( range(5), 3, True ) )
        self.assertEqual( comb53, [
            (0, 1, 2),
            (0, 1, 3),
            (0, 1, 4),
            (0, 2, 3), 
            (0, 2, 4),
            (0, 3, 4),
            (1, 2, 3),
            (1, 2, 4),
            (1, 3, 4),
            (2, 3, 4)
        ])

    def test_combdifflen(self):
        N = [3, 5]
        result = list(collider._combinationsDiffLen(N) )
        assert len(result) == 3*5
        assert result == [[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [2, 0], [2, 1], [2, 2], [2, 3], [2, 4]]
        #
        N = [2, 2, 1]
        result = list(collider._combinationsDiffLen(N) )
        assert len(result) == 4
        assert result == [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 0]]
        #
        N = [3, 5, 9]
        result = list(collider._combinationsDiffLen(N) )
        assert len(result) == 3*9*5
        assert result == [[0, 0, 0], [0, 0, 1], [0, 0, 2], [0, 0, 3], [0, 0, 4], [0, 0, 5], [0, 0, 6], [0, 0, 7], [0, 0, 8], [0, 1, 0], [0, 1, 1], [0, 1, 2], [0, 1, 3], [0, 1, 4], [0, 1, 5], [0, 1, 6], [0, 1, 7], [0, 1, 8], [0, 2, 0], [0, 2, 1], [0, 2, 2], [0, 2, 3], [0, 2, 4], [0, 2, 5], [0, 2, 6], [0, 2, 7], [0, 2, 8], [0, 3, 0], [0, 3, 1], [0, 3, 2], [0, 3, 3], [0, 3, 4], [0, 3, 5], [0, 3, 6], [0, 3, 7], [0, 3, 8], [0, 4, 0], [0, 4, 1], [0, 4, 2], [0, 4, 3], [0, 4, 4], [0, 4, 5], [0, 4, 6], [0, 4, 7], [0, 4, 8], [1, 0, 0], [1, 0, 1], [1, 0, 2], [1, 0, 3], [1, 0, 4], [1, 0, 5], [1, 0, 6], [1, 0, 7], [1, 0, 8], [1, 1, 0], [1, 1, 1], [1, 1, 2], [1, 1, 3], [1, 1, 4], [1, 1, 5], [1, 1, 6], [1, 1, 7], [1, 1, 8], [1, 2, 0], [1, 2, 1], [1, 2, 2], [1, 2, 3], [1, 2, 4], [1, 2, 5], [1, 2, 6], [1, 2, 7], [1, 2, 8], [1, 3, 0], [1, 3, 1], [1, 3, 2], [1, 3, 3], [1, 3, 4], [1, 3, 5], [1, 3, 6], [1, 3, 7], [1, 3, 8], [1, 4, 0], [1, 4, 1], [1, 4, 2], [1, 4, 3], [1, 4, 4], [1, 4, 5], [1, 4, 6], [1, 4, 7], [1, 4, 8], [2, 0, 0], [2, 0, 1], [2, 0, 2], [2, 0, 3], [2, 0, 4], [2, 0, 5], [2, 0, 6], [2, 0, 7], [2, 0, 8], [2, 1, 0], [2, 1, 1], [2, 1, 2], [2, 1, 3], [2, 1, 4], [2, 1, 5], [2, 1, 6], [2, 1, 7], [2, 1, 8], [2, 2, 0], [2, 2, 1], [2, 2, 2], [2, 2, 3], [2, 2, 4], [2, 2, 5], [2, 2, 6], [2, 2, 7], [2, 2, 8], [2, 3, 0], [2, 3, 1], [2, 3, 2], [2, 3, 3], [2, 3, 4], [2, 3, 5], [2, 3, 6], [2, 3, 7], [2, 3, 8], [2, 4, 0], [2, 4, 1], [2, 4, 2], [2, 4, 3], [2, 4, 4], [2, 4, 5], [2, 4, 6], [2, 4, 7], [2, 4, 8]]


if __name__ == '__main__':
    unittest.main()

