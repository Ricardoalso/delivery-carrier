This module adds the possibility to flag some measurements on package to be required for delivery.
It depends on the `stock_quant_package_dimension` which adds some dimension on pacakges.

A new tab is displayed on shipping methods for the configuration.
The dimensions can be set on the wizard displayed when the Put In Pack button is clicked.
A check is done on validation of a stock.picking, to ensure that the required measurements are properly set.
