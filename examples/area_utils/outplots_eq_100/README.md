Look at plot region7.png
Now compare the same irregular region in plot all_regions.png.

You can see the some missing or masked over 3 to 4 pixels. Isnt it ?

Reason :
=======

The exact reason for this is,
    first region7 was extracted and updated mask of input data (because 
    we passed argument update_mask=True) and then only region9 was extracted.
    
    While applying region9's mask out side of irregular boundary region,
    region7's visible data was masked. 
    
    If you read the algorithm you can understand.
    
But still you can access particular regions by calling function 
irregularClosedRegionSelector to manipulate your region wise data.

So this kind of problem will occur one and only when you do update_mask=True
and plot original data.

Solution :
==========

To overcome above problem, just extract individual irregular regions by 
function calling irregularClosedRegionSelector and plot it in loop as shown
in real_demo2.py 

Arulalan.T
15.07.2014
