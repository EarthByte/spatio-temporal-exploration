The edited script now takes care of the duplicate rows that were generated in subStats_*.csv substantially reducing the data by more than half.
<br>So effectively coregLoop runs more than two times faster now. 
<br>8 lines of code have been added in the end and a new outputfile2 has been introduced in the script 

<br><b> Please note that pointlist manually picked out in the script coregLoop needs to be changed. 
<br> For example:- </b> For Andes it was pointlist=lonlat[379:,0:2] and now it's lonlat[78:0,2] to get the same shape of the subduction zone. 
