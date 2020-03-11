Last updated: 24 January 2020
v 1.0 - Initial set of files
v 1.1 - Separating topological lines gpml from the global plate topology file
v 1.2 - Removed passive margin geometry from plate topologies in the Western Tethys from ~200 to 128 Ma
v 1.3 - Removed overlapping plate topology in Western Tethys 
v 1.4 - Updated geometry for Woyla terrane, Fixed static polygon issue in Arctic
v 1.5 - Fixed Pacific plate velocity artefact at ~57 Ma
v 1.6 - Fixed Mascarene Basin plate boundary in Late Cretaceous, and minor fixes to the static polygons
v 1.7 - Fixed overlap of Luzon with Zamboanga
v 1.8 - Included rotations from North Atlantic model of Barnett-Moore et al. (2018), Basin Research
v 1.9 - Fixed Pacific rotation at chron 25 (~56 Ma)
v 1.10 - Fixed South Philippine Sea Plate plate id at 35 Ma
v 1.11 - Introduced a back-arc opening scenario in Western Tethys north of Arabia. See Note 1 below.
v 1.12 - Fixed overlaps of Eurasian topologies over Greenland for 62-63 Ma, 65-67 and 70 Ma​. 
v 1.13 - Fixed plate topologies from 65 Ma to present north and east of Madagascar.
v 1.14 - Plate topology segments have been QC-ed and duplicated clones removed from use by topologies. This helps with computing plate boundary lengths, and makes plotting plate boundaries neater. 
v 1.15 - Fixed incorrect rotations for the Pacific plate prior to 83 Ma and implemented the rotations of Torsvik et al. (2019)
v 1.16 - Fixed topology breaks in souther Pacific in the mid Cretaceous 

This directory contains files associated with the paper:
Müller, R.D., Seton, M., Zahirovic, S., Williams, S.E., Matthews, K.J., Wright, N.M., Shephard, G.E., Maloney, K.T., Barnett-Moore, N., Hosseinpour, M., Bower, D.J., Cannon, J., InPress. Ocean basin evolution and global-scale plate reorganization events since Pangea breakup, AREPS

The latest version of this supplementary dataset can be downloaded from:
http://www.earthbyte.org/ocean-basin-evolution-and-global-scale-plate-reorganization-events-since-pangea-breakup/ 

This directory contains five files and two folders:

Global_EarthByte_230-0Ma_GK07_AREPS_PlateBoundaries.gpml - contains a topological network of plate polygons with dynamic geometries in .gpml format (native GPlates Markup Language format)
Global_EarthByte_230-0Ma_GK07_AREPS_Topology_BuildingBlocks.gpml - contains topological lines that participate in plate topologies in .gpml format (native GPlates Markup Language format)
Global_EarthByte_230-0Ma_GK07_AREPS.rot - contains the reconstruction poles that describe the motions of the continents and oceans
Global_EarthByte_230-0Ma_GK07_AREPS_Coastlines.gpml - contains the present-day coastline file that can be reconstructed through time.
Global_EarthByte_Plate_ID_Table_AREPS.xlsx - excel table with a description of the plate identifications used in the plate model.  
Shapefile/ - contains a shapefile of the above coastlines and a static polygon file, which can be used to cookie-cut data or reconstruct rasters.
AgeGridInput/ - contains files needed to make agegrids.

To load the files in GPlates do the following:
1.  Open GPlates
2.  Pull down the GPlates File menu and select the operation Open Feature Collection
3.  Click the files that you want to load e.g. the .rot rotation file and .gpml files
4.  Click Open 
Alternatively, drag and drop the files onto the globe.

Play around with the GPlates buttons to make an animation, select features, draw features, etc.  
For more information, read the GPlates manual which can be downloaded from www.gplates.org or http://www.earthbyte.org/Resources/earthbyte_gplates.html

When wanting to isolate the display of the plate topologies, hide the relevant Reconstructed Geometries (green) entry in the GPlates Layers window, as well as the  "Global_EarthByte_230-0Ma_GK07_AREPS_Topology_BuildingBlocks.gpml" Resolved Topological Geometries (purple) entry.

Any questions, please email: dietmar.muller@sydney.edu.au, maria.seton@sydney.edu.au or sabin.zahirovic@sydney.edu.au

Note 1 - Western Tethys
The Western Tethys, north of Arabia, is punctuated by ophiolite formation and obduction in Cretaceous times. The first end-member involves applying the central and eastern Tethys analogues of back-arc opening and closure following ophiolite obduction, much like is usually implied in the Kohistan-Ladakh and Greater India collision zone. This scenario makes the Western Tethys north of Arabia consistent with the model of the eastern Tethys. However, a second end-member interpretation for the formation of many of the ophiolites in the region is that they develop when a mid-oceanic ridge inverts to become a subduction zone. Both options are plausible, but we implemented a change in this plate model after it was published to reflect the first end-member scenario in order to link the region to the eastern Tethys in a plausible way. This scenario is based on back-arc opening from ~125 Ma (Jolivet et al., 2016), with subduction of back-arc initiating in Albian times from ~110 Ma (Ghazi et at., 2003; Aygul et al., 2015). Obduction and Arabia collision with an arc occurs at 85 Ma (Jolivet et al., 2016; Jagoutz et al., 2016). The scenario is also consistent with the recent work of Morris et al. (2016) on the Oman Ophiolite. This change is also reflected in the rotation and plate topology files.
 


