import unittest
from esdcs import esdcIo
from g3.annotation_to_ggg import collapse_null_nodes
from g3.esdcs_to_ggg import ggg_from_esdc

class TestCase(unittest.TestCase):


    def testCollapseNullNodes(self):
        esdcs = esdcIo.parse("""
- Pick up the tire pallet.
- - EVENT:
     r: Pick up
     l: the tire pallet
""")
        esdc = esdcs[0]

        ggg = ggg_from_esdc(esdc)
        ggg.to_latex("test.pdf")



        esdcs = esdcIo.parse("""
- Pick up the tire pallet near the box pallet.
- - EVENT:
     r: Pick up
     l: 
        OBJECT:
           f:  the tire pallet
           r:  near
           l:  the box pallet
""")
        esdc = esdcs[0]

        ggg = ggg_from_esdc(esdc)
        ggg.to_latex("test.pdf")


        esdcs = esdcIo.parse("""
- Put the tire pallet on the truck.
- - EVENT:
     r: Put
     l: the tire pallet
     l2:
        PLACE:
           r: 'on'
           l: the truck
""")
        esdc = esdcs[0]

        ggg = ggg_from_esdc(esdc)
        ggg.to_latex("test.pdf")

        esdcs = esdcIo.parse("""
- Pick up the tire pallet near the truck.
- - EVENT:
      r: Pick up
      l:
        OBJECT: {f: the tire pallet, r: near, l: the truck}
""")
        esdc = esdcs[0]
        ggg = ggg_from_esdc(esdc)
        ggg.to_latex("test.pdf")
        ggg.to_file("test_dot.pdf")


        self.fail()
        
