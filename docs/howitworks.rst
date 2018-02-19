How it works
============

Overview
--------

The scripts reads the Eclipse files or ROFF files and computes HCPV thickness
or weighted average of a property, per cell, layer by layer.

.. image:: images/gridding_approach.png

Then the value and position of each 3D cell (per layer) is
then gridded by a scipy/matplotlib method to form a regular map.

For HC thickness, the maps per layers are then summed, to form a
sum hc thickness map per zone or by all zones that are spesified.


Options for HC thickness
------------------------

In the HC thickness settings there are some optins that need explanation:

Method "use_poro"
^^^^^^^^^^^^^^^^^

Given Eclipse kewords, the HC thickness is based on
PORO, NTG, DZ, SHC, where SHC is SOIL or SGAS. The hydrocarbon
fraction (e.g. oil) is then multiplied with the cell thickness::

 HCPFDZ =  PORO * NTG * SOIL * DZ

Method "use_porv"
^^^^^^^^^^^^^^^^^

Uses the PORV instead::

 AREA = DX * DY
 HCPFDZ = PORV * SOIL / AREA

Method "dz_only"
^^^^^^^^^^^^^^^^^

This is a specal version, looking at BULK thickness, *not* NET thcikness. All
rock outside a specified saturation interval will a weight zero in the computation.


Further details
---------------

Contact JRIV@statoil.com for further details.
