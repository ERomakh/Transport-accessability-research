# -*- coding: utf-8 -*-
import arcpy
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Urban transport research"
        self.alias = "Urban transport research"
        # List of tool classes associated with this toolbox
        self.tools = [Route_script, Split_by_District, General_access ,Local_access, Walking_access]

class Route_script(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Route_script"
        self.description = "Route_script"
        self.canRunInBackground = True
    def getParameterInfo(self):
        """Define parameter definitions"""
        network_dataset = arcpy.Parameter(
            displayName="Input OSM Network Dataset",
            name="network_dataset",
            datatype="DENetworkDataset",
            parameterType="Required",
            direction="Input")

        stops = arcpy.Parameter(
            displayName="Stops",
            name="stops",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        routes = arcpy.Parameter(
            displayName="Bus routes",
            name="routes",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")


        params = [network_dataset, stops, routes]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        network_dataset = parameters[0].valueAsText
        stops = parameters[1].valueAsText
        routes = parameters[2].valueAsText

        #Creating output file
        arcpy.env.workspace = r'Z:\Documents\Network_an\Diplom\Nov30.gdb'
        arcpy.env.overwriteOutput = True
        output = r'D:\Diplom\Diplom.gdb\lines'
        bus_lines = arcpy.CreateFeatureclass_management(r'Z:\Documents\Network_an\Diplom\Nov30.gdb', 'Bus_Routes', 'POLYLINE',
                                                        spatial_reference=r'Z:\Documents\Network_an\Diplom\Diplom.gdb\stops_nov11')
        arcpy.MakeFeatureLayer_management(bus_lines, "bus_lines")
        arcpy.AddField_management('bus_lines', 'Route_name', 'TEXT')

        num_list = []
        arcpy.CreateFeatureclass_management(arcpy.env.workspace, 'points', 'POINT', spatial_reference =
                                            r'Z:\Documents\Network_an\Diplom\Diplom.gdb\stops_nov11')
        points = 'points'
        out_gdb = arcpy.env.workspace
        #Stops in general, points are specifics stops by routes
        stops_lyr = arcpy.MakeFeatureLayer_management(stops, "bus_stops")
        arcpy.MakeFeatureLayer_management(points, "points")
        #List of buses
        field = ['Route_num']
        with arcpy.da.SearchCursor(stops, field) as cursor:
            for row in cursor:
                num_list.append(row[0])
        setted = set(num_list)
        arcpy.AddMessage(len(setted))
        arcpy.SetProgressor('step', 'Creating bus routes', 0, len(setted), 1)
        count_num = 0
        #Creating route
        for x in setted:
            try:
                arcpy.SetProgressorLabel("Creating {0}...".format(x))
                arcpy.AddMessage('Bus route = {0}'.format(x))
                #arcpy.AddMessage(arcpy.GetCount_management('bus_stops'))
                arcpy.SelectLayerByAttribute_management(stops_lyr, 'NEW_SELECTION', "Route_num = '{0}'".format(x))
                arcpy.FeatureClassToFeatureClass_conversion(stops_lyr, r'Z:\Documents\Network_an\Diplom\Nov30.gdb',
                                                            out_name = "curr_stops")
                arcpy.AddMessage('Number of stops in current route = {0}'.format(arcpy.GetCount_management(r'Z:\Documents\Network_an\Diplom\Nov30.gdb\curr_stops')))
                arcpy.AddMessage('Progressor = {0}'.format(count_num))
                arcpy.MakeODCostMatrixLayer_na(in_network_dataset="Test_Routes_ND",
                                            out_network_analysis_layer="OD Cost Matrix", impedance_attribute="Minutes",
                                            default_cutoff="", default_number_destinations_to_find="",
                                            accumulate_attribute_name="", UTurn_policy="ALLOW_UTURNS",
                                            restriction_attribute_name="Oneway", hierarchy="NO_HIERARCHY",
                                            hierarchy_settings="", output_path_shape="STRAIGHT_LINES", time_of_day="")
                arcpy.AddLocations_na(in_network_analysis_layer="OD Cost Matrix", sub_layer="Origins",
                                    in_table="curr_stops",
                                    field_mappings="Name Name #;CurbApproach CurbApproach 0;TargetDestinationCount TargetDestinationCount #;Cutoff_Length Cutoff_Length #",
                                    search_tolerance="200 Meters", sort_field="",
                                    search_criteria="tested_roads SHAPE;Test_Routes_ND_Junctions NONE",
                                    match_type="MATCH_TO_CLOSEST", append="APPEND",
                                    snap_to_position_along_network="NO_SNAP", snap_offset="5 Meters",
                                    exclude_restricted_elements="INCLUDE",
                                    search_query="tested_roads #;Test_Routes_ND_Junctions #")
                arcpy.AddLocations_na(in_network_analysis_layer="OD Cost Matrix", sub_layer="Destinations",
                                    in_table="curr_stops",
                                    field_mappings="Name Name #;CurbApproach CurbApproach 0;TargetDestinationCount TargetDestinationCount #;Cutoff_Length Cutoff_Length #",
                                    search_tolerance="200 Meters", sort_field="",
                                    search_criteria="tested_roads SHAPE;Test_Routes_ND_Junctions NONE",
                                    match_type="MATCH_TO_CLOSEST", append="APPEND",
                                    snap_to_position_along_network="NO_SNAP", snap_offset="5 Meters",
                                    exclude_restricted_elements="INCLUDE",
                                    search_query="tested_roads #;Test_Routes_ND_Junctions #")
                arcpy.na.GenerateOriginDestinationCostMatrix('Origins', 'Destinations', network_dataset,out_gdb, 'OD_lines', 'Loc_or', 'Loc_dest')
                arcpy.na.Solve("OD Cost Matrix")
                #break
                #Save Locations
                arcpy.FeatureClassToFeatureClass_conversion(in_features="OD Cost Matrix\Lines",
                                                            out_path=r'Z:\Documents\Network_an\Diplom\Nov30.gdb',
                                                            out_name="OD_lines2")
                #Split names
                OD_lines2 = r'Z:\Documents\Network_an\Diplom\Nov30.gdb\OD_lines2'
                arcpy.MakeFeatureLayer_management(OD_lines2, "OD_lines2")
                arcpy.AddField_management('OD_lines2', 'Location1', 'TEXT')
                arcpy.AddField_management('OD_lines2', 'Location2', 'TEXT')
                arcpy.CalculateField_management(in_table="OD_lines2", field="Location1", expression="[Name]",
                                                expression_type="VB", code_block="")
                arcpy.CalculateField_management(in_table="OD_lines2", field="Location2", expression="[Name]",
                                                expression_type="VB", code_block="")
                arcpy.CalculateField_management(in_table="OD_lines2", field="Location1", expression="!Location1! .rsplit(' - ')[0]",
                                                expression_type="PYTHON_9.3", code_block="")
                arcpy.CalculateField_management(in_table="OD_lines2", field="Location2", expression="!Location2! .rsplit(' - ')[1]",
                                                expression_type="PYTHON_9.3", code_block="")
                #Biggest distance
                arcpy.Sort_management(in_dataset="OD_lines2",
                                    out_dataset=r'Z:\Documents\Network_an\Diplom\Nov30.gdb\MaxMin',
                                    sort_field="Total_Minutes DESCENDING", spatial_sort_method="UR")
                MLoc1 = []
                MLoc2 = []
                fld = ['Location1', 'Location2']
                MaxMin = r'Z:\Documents\Network_an\Diplom\Nov30.gdb\MaxMin'
                with arcpy.da.SearchCursor(MaxMin, fld) as cursor:
                    for row in cursor:
                        MLoc1.append(row[0])
                        MLoc2.append(row[1])
                #Creating origin and destination points of Route
                Loc_or = r'Z:\Documents\Network_an\Diplom\Nov30.gdb\Loc_or'
                arcpy.MakeFeatureLayer_management(Loc_or, "Loc_or")
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="Loc_or", selection_type="NEW_SELECTION",
                                                        where_clause="Name = '{0}'".format(MLoc1[0]))
                arcpy.FeatureClassToFeatureClass_conversion("Loc_or", r'Z:\Documents\Network_an\Diplom\Nov30.gdb',
                                                            out_name="originroute")
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="Loc_or", selection_type="CLEAR_SELECTION")
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="Loc_or", selection_type="NEW_SELECTION",
                                                        where_clause="Name = '{0}'".format(MLoc2[0]))
                arcpy.FeatureClassToFeatureClass_conversion("Loc_or", r'Z:\Documents\Network_an\Diplom\Nov30.gdb',
                                                            out_name="destroute")
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="Loc_or", selection_type="CLEAR_SELECTION")
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="Loc_or", selection_type="NEW_SELECTION",
                                                        where_clause="Name = '{0}'".format(MLoc1[0]))
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="Loc_or", selection_type="ADD_TO_SELECTION",
                                                        where_clause="Name = '{0}'".format(MLoc2[0]))
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="Loc_or", selection_type="SWITCH_SELECTION")
                arcpy.FeatureClassToFeatureClass_conversion("Loc_or", r'Z:\Documents\Network_an\Diplom\Nov30.gdb',
                                                            out_name="middlepoints")
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="Loc_or", selection_type="CLEAR_SELECTION")
                #Creating Route task
                arcpy.MakeRouteLayer_na(in_network_dataset="Test_Routes_ND", out_network_analysis_layer="Route",
                                        impedance_attribute="Length", find_best_order="USE_INPUT_ORDER",
                                        ordering_type="PRESERVE_BOTH", time_windows="NO_TIMEWINDOWS",
                                        accumulate_attribute_name="", UTurn_policy="ALLOW_UTURNS",
                                        restriction_attribute_name="Oneway", hierarchy="NO_HIERARCHY",
                                        hierarchy_settings="", output_path_shape="TRUE_LINES_WITH_MEASURES",
                                        start_date_time="")
                arcpy.AddLocations_na(in_network_analysis_layer="Route", sub_layer="Stops",
                                    in_table=r'Z:\Documents\Network_an\Diplom\Nov30.gdb\originroute',
                                    field_mappings="Name Name #;CurbApproach CurbApproach 0",
                                    search_tolerance="200 Meters", sort_field="",
                                    search_criteria="tested_roads SHAPE;Test_Routes_ND_Junctions NONE",
                                    match_type="MATCH_TO_CLOSEST", append="APPEND",
                                    snap_to_position_along_network="NO_SNAP", snap_offset="5 Meters",
                                    exclude_restricted_elements="INCLUDE",
                                    search_query="tested_roads #;Test_Routes_ND_Junctions #")
                arcpy.AddLocations_na(in_network_analysis_layer="Route", sub_layer="Stops",
                                    in_table=r'Z:\Documents\Network_an\Diplom\Nov30.gdb\middlepoints',
                                    field_mappings="Name Name #;CurbApproach CurbApproach 0",
                                    search_tolerance="200 Meters", sort_field="",
                                    search_criteria="tested_roads SHAPE;Test_Routes_ND_Junctions NONE",
                                    match_type="MATCH_TO_CLOSEST", append="APPEND",
                                    snap_to_position_along_network="NO_SNAP", snap_offset="5 Meters",
                                    exclude_restricted_elements="INCLUDE",
                                    search_query="tested_roads #;Test_Routes_ND_Junctions #")
                arcpy.AddLocations_na(in_network_analysis_layer="Route", sub_layer="Stops",
                                    in_table=r'Z:\Documents\Network_an\Diplom\Nov30.gdb\destroute',
                                    field_mappings="Name Name #;CurbApproach CurbApproach 0",
                                    search_tolerance="200 Meters", sort_field="",
                                    search_criteria="tested_roads SHAPE;Test_Routes_ND_Junctions NONE",
                                    match_type="MATCH_TO_CLOSEST", append="APPEND",
                                    snap_to_position_along_network="NO_SNAP", snap_offset="5 Meters",
                                    exclude_restricted_elements="INCLUDE",
                                    search_query="tested_roads #;Test_Routes_ND_Junctions #")
                arcpy.na.FindRoutes('Stops', 'Meters', 'Test_Routes_ND', r'Z:\Documents\Network_an\Diplom\Nov30.gdb',
                                    'OutRoutes', 'OutEdges', 'OutDirections', 'OutStops',
                                    Reorder_Stops_to_Find_Optimal_Routes = 'FIND_BEST_ORDER',
                                    Preserve_Terminal_Stops = 'PRESERVE_BOTH')
                #Creating Output file
                arcpy.Append_management(inputs=r'Z:\Documents\Network_an\Diplom\Nov30.gdb\OutRoutes', target=bus_lines,
                                        schema_type="NO_TEST")
                unique_OID = []
                field_OD = ['OBJECTID']
                with arcpy.da.SearchCursor(bus_lines, field_OD) as cursor:
                    for row in cursor:
                        unique_OID.append(row[0])
                arcpy.AddMessage(max(unique_OID))
                with arcpy.da.UpdateCursor(bus_lines, ['OBJECTID', 'Route_name']) as cursor:
                    for row in cursor:
                        if row[0] == max(unique_OID):
                            row[1] = x
                            cursor.updateRow(row)
                #for row in rows:
                #    if row[0] == max(unique_OID):
                #        row[1] = x
                #rows.updateRow(row)
                #del row, rows
                arcpy.SelectLayerByAttribute_management(stops_lyr, 'CLEAR_SELECTION')
                arcpy.SetProgressorPosition()
                count_num += 1
            except:
                arcpy.AddMessage('Something goes wrong')
                arcpy.AddMessage(arcpy.GetMessages())
        arcpy.ResetProgressor()

class Split_by_District(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Point_population"
        self.description = "Point_population"
        self.canRunInBackground = True
    def getParameterInfo(self):
        """Define parameter definitions"""
        points = arcpy.Parameter(
            displayName="Input points",
            name="district",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        params = [points]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        points = parameters[0].valueAsText

        #Variables
        points_lyr = arcpy.MakeFeatureLayer_management(points, "points")

        #List of values
        points_list = []
        field = ['OKATO']
        with arcpy.da.SearchCursor(points, field) as cursor:
            for row in cursor:
                points_list.append(row[0])

        #Selection
        for element in points_list:
            arcpy.SelectLayerByAttribute_management(in_layer_or_view=points_lyr, selection_type="NEW_SELECTION",
                                                    where_clause="OKATO = '{0}'".format(element))
            with arcpy.da.UpdateCursor(points, ['OKATO','Population','Point_popul']) as cursor:
                for row in cursor:
                    if row[0] == element:
                        row[2] = (row[1]/points_list.count(element))
                        cursor.updateRow(row)

class General_access(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "General_access"
        self.description = "General_access"
        self.canRunInBackground = True
    def getParameterInfo(self):
        """Define parameter definitions"""
        center_point = arcpy.Parameter(
            displayName="Input center point",
            name="center_point",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        network_dataset = arcpy.Parameter(
            displayName="Input Network Dataset",
            name="network_dataset",
            datatype="DENetworkDataset",
            parameterType="Required",
            direction="Input")

        popul_points = arcpy.Parameter(
            displayName="Input population points",
            name="popul_points",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        points_30 = arcpy.Parameter(
            displayName="Population 30 min",
            name="points_30",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        points_45 = arcpy.Parameter(
            displayName="Population 45 min",
            name="points_45",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        points_60 = arcpy.Parameter(
            displayName="Population 60 min",
            name="points_60",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        params = [center_point, network_dataset, popul_points, points_30, points_45, points_60]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        center_point = parameters[0].valueAsText
        network_dataset = parameters[1].valueAsText
        popul_points = parameters[2].valueAsText
        points_30 = parameters[3].valueAsText
        points_45 = parameters[4].valueAsText
        points_60 = parameters[5].valueAsText

        #Variables
        arcpy.env.workspace = r'Z:\Documents\Network_an\Diplom\Common_access.gdb'
        arcpy.env.overwriteOutput = True

        center_point_lyr = arcpy.MakeFeatureLayer_management(center_point, "center_point")
        popul_points_lyr = arcpy.MakeFeatureLayer_management(popul_points, "popul_points")

        SA30 = arcpy.CreateFeatureclass_management('Z:\Documents\Network_an\Diplom\Common_access.gdb', 'SA30', "POINT")
        #SA30 = 'in_memory\SA30'
        SA30lyr = arcpy.MakeFeatureLayer_management(SA30, "SA30")

        SA45 = arcpy.CreateFeatureclass_management('Z:\Documents\Network_an\Diplom\Common_access.gdb', 'SA45', "POINT")
        #SA45 = 'in_memory\SA45'
        SA45lyr = arcpy.MakeFeatureLayer_management(SA45, "SA45")

        SA60 = arcpy.CreateFeatureclass_management('Z:\Documents\Network_an\Diplom\Common_access.gdb', 'SA60', "POINT")
        #SA60 = 'in_memory\SA60'
        SA60lyr = arcpy.MakeFeatureLayer_management(SA60, "SA60")

        #Network 30
        arcpy.MakeServiceAreaLayer_na(in_network_dataset=network_dataset, out_network_analysis_layer="Service Area30",
                                      impedance_attribute="Minutes", travel_from_to="TRAVEL_FROM",
                                      default_break_values="30", polygon_type="SIMPLE_POLYS", merge="MERGE",
                                      nesting_type="RINGS", line_type="NO_LINES", overlap="OVERLAP", split="NO_SPLIT",
                                      excluded_source_name="", accumulate_attribute_name="",
                                      UTurn_policy="ALLOW_UTURNS", restriction_attribute_name="",
                                      polygon_trim="TRIM_POLYS", poly_trim_value="500 Meters",
                                      lines_source_fields="NO_LINES_SOURCE_FIELDS", hierarchy="NO_HIERARCHY",
                                      time_of_day="")
        arcpy.AddLocations_na(in_network_analysis_layer="Service Area30", sub_layer="Facilities", in_table=center_point_lyr,
                              field_mappings="", search_tolerance="100 Meters", sort_field="",
                              search_criteria="SPrConnections2022 SHAPE;SPrGround2022 SHAPE;SPrMetro2022 SHAPE;feature2022_ND_Junctions NONE",
                              match_type="MATCH_TO_CLOSEST", append="APPEND", snap_to_position_along_network="NO_SNAP",
                              snap_offset="5 Meters", exclude_restricted_elements="INCLUDE",
                              search_query="SPrConnections2022 #;SPrGround2022 #;SPrMetro2022 #;feature2022_ND_Junctions #")
        arcpy.na.GenerateServiceAreas(center_point_lyr, "30", "Minutes", network_dataset, SA30lyr)
        arcpy.na.Solve("Service Area30")

        #Network 45
        arcpy.MakeServiceAreaLayer_na(in_network_dataset=network_dataset, out_network_analysis_layer="Service Area45",
                                      impedance_attribute="Minutes", travel_from_to="TRAVEL_FROM",
                                      default_break_values="45", polygon_type="SIMPLE_POLYS", merge="MERGE",
                                      nesting_type="RINGS", line_type="NO_LINES", overlap="OVERLAP", split="NO_SPLIT",
                                      excluded_source_name="", accumulate_attribute_name="",
                                      UTurn_policy="ALLOW_UTURNS", restriction_attribute_name="",
                                      polygon_trim="TRIM_POLYS", poly_trim_value="500 Meters",
                                      lines_source_fields="NO_LINES_SOURCE_FIELDS", hierarchy="NO_HIERARCHY",
                                      time_of_day="")
        arcpy.AddLocations_na(in_network_analysis_layer="Service Area45", sub_layer="Facilities",
                              in_table=center_point_lyr,
                              field_mappings="", search_tolerance="100 Meters", sort_field="",
                              search_criteria="SPrConnections2022 SHAPE;SPrGround2022 SHAPE;SPrMetro2022 SHAPE;feature2022_ND_Junctions NONE",
                              match_type="MATCH_TO_CLOSEST", append="APPEND", snap_to_position_along_network="NO_SNAP",
                              snap_offset="5 Meters", exclude_restricted_elements="INCLUDE",
                              search_query="SPrConnections2022 #;SPrGround2022 #;SPrMetro2022 #;feature2022_ND_Junctions #")
        arcpy.na.GenerateServiceAreas(center_point_lyr, "45", "Minutes", network_dataset, SA45lyr)
        arcpy.na.Solve("Service Area45")

        #Network 60
        arcpy.MakeServiceAreaLayer_na(in_network_dataset=network_dataset, out_network_analysis_layer="Service Area60",
                                      impedance_attribute="Minutes", travel_from_to="TRAVEL_FROM",
                                      default_break_values="60", polygon_type="SIMPLE_POLYS", merge="MERGE",
                                      nesting_type="RINGS", line_type="NO_LINES", overlap="OVERLAP", split="NO_SPLIT",
                                      excluded_source_name="", accumulate_attribute_name="",
                                      UTurn_policy="ALLOW_UTURNS", restriction_attribute_name="",
                                      polygon_trim="TRIM_POLYS", poly_trim_value="500 Meters",
                                      lines_source_fields="NO_LINES_SOURCE_FIELDS", hierarchy="NO_HIERARCHY",
                                      time_of_day="")
        arcpy.AddLocations_na(in_network_analysis_layer="Service Area60", sub_layer="Facilities",
                              in_table=center_point_lyr,
                              field_mappings="", search_tolerance="100 Meters", sort_field="",
                              search_criteria="SPrConnections2022 SHAPE;SPrGround2022 SHAPE;SPrMetro2022 SHAPE;feature2022_ND_Junctions NONE",
                              match_type="MATCH_TO_CLOSEST", append="APPEND", snap_to_position_along_network="NO_SNAP",
                              snap_offset="5 Meters", exclude_restricted_elements="INCLUDE",
                              search_query="SPrConnections2022 #;SPrGround2022 #;SPrMetro2022 #;feature2022_ND_Junctions #")
        arcpy.na.GenerateServiceAreas(center_point_lyr, "60", "Minutes", network_dataset, SA60lyr)
        arcpy.na.Solve("Service Area60")

        #Intersect 30
        pre_points_30 = arcpy.CreateFeatureclass_management("Z:\Documents\Network_an\Diplom\Common_access.gdb", 'pre_points_30',
                                                            "POINT")
        pre_points_30_lyr = arcpy.MakeFeatureLayer_management(pre_points_30, "pre_points_30")
        arcpy.Intersect_analysis([popul_points_lyr, SA30lyr], pre_points_30_lyr, "ALL", "", "point")

        #Intersect 45
        pre_points_45 = arcpy.CreateFeatureclass_management("Z:\Documents\Network_an\Diplom\Common_access.gdb", 'pre_points_45',
                                                            "POINT")
        pre_points_45_lyr = arcpy.MakeFeatureLayer_management(pre_points_45, "pre_points_45")
        arcpy.Intersect_analysis([popul_points_lyr, SA45lyr], pre_points_45_lyr, "ALL", "", "point")

        #Intersect 60
        pre_points_60 = arcpy.CreateFeatureclass_management("Z:\Documents\Network_an\Diplom\Common_access.gdb", 'pre_points_60',
                                                            "POINT")
        pre_points_60_lyr = arcpy.MakeFeatureLayer_management(pre_points_60, "pre_points_60")
        arcpy.Intersect_analysis([popul_points_lyr, SA60lyr], pre_points_60_lyr, "ALL", "", "point")

        #Create output
        arcpy.CreateFeatureclass_management("Z:\Documents\Network_an\Diplom\Common_access.gdb",'points_30',
                                            'MULTIPOINT',
                                            spatial_reference = "Z:\Documents\Network_an\Diplom\Common_access.gdb\center_point")
        arcpy.CreateFeatureclass_management("Z:\Documents\Network_an\Diplom\Common_access.gdb", 'points_45',
                                            'MULTIPOINT',
                                            spatial_reference = "Z:\Documents\Network_an\Diplom\Common_access.gdb\center_point")
        arcpy.CreateFeatureclass_management("Z:\Documents\Network_an\Diplom\Common_access.gdb", 'points_60', 'MULTIPOINT',
                                            spatial_reference = "Z:\Documents\Network_an\Diplom\Common_access.gdb\center_point")

        #Dissolve_30
        arcpy.Dissolve_management(in_features=pre_points_30_lyr,
                                  out_feature_class=points_30,
                                  dissolve_field="FacilityID", statistics_fields="Point_popul SUM",
                                  multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
        # Dissolve_45
        arcpy.Dissolve_management(in_features=pre_points_45,
                                  out_feature_class=points_45,
                                  dissolve_field="FacilityID", statistics_fields="Point_popul SUM",
                                  multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
        # Dissolve_60
        arcpy.Dissolve_management(in_features=pre_points_60,
                                  out_feature_class=points_60,
                                  dissolve_field="FacilityID", statistics_fields="Point_popul SUM",
                                  multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

class Local_access(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Local_access"
        self.description = "Local_access"
        self.canRunInBackground = True
    def getParameterInfo(self):
        """Define parameter definitions"""
        metro_stations = arcpy.Parameter(
            displayName="Input metro stations",
            name="center_point",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        network_dataset = arcpy.Parameter(
            displayName="Input Network Dataset",
            name="network_dataset",
            datatype="DENetworkDataset",
            parameterType="Required",
            direction="Input")

        popul_points = arcpy.Parameter(
            displayName="Input population points",
            name="popul_points",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        districts = arcpy.Parameter(
            displayName="Input municipal districts",
            name="points_30",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        populated_area5 = arcpy.Parameter(
            displayName="Output populated area 5 min",
            name="populated_area5",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        populated_area10 = arcpy.Parameter(
            displayName="Output populated area 10 min",
            name="populated_area10",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")

        populated_area15 = arcpy.Parameter(
            displayName="Output populated area 15 min",
            name="populated_area15",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")


        params = [metro_stations, network_dataset, popul_points, districts, populated_area5, populated_area10, populated_area15]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        metro_stations = parameters[0].valueAsText
        network_dataset = parameters[1].valueAsText
        popul_points = parameters[2].valueAsText
        districts = parameters[3].valueAsText
        populated_area5 = parameters[4].valueAsText
        populated_area10 = parameters[5].valueAsText
        populated_area15 = parameters[6].valueAsText

        # Variables
        arcpy.env.workspace = r'Z:\Documents\Network_an\Diplom\local_access.gdb'
        arcpy.env.overwriteOutput = True
        metro_stations_lyr = arcpy.MakeFeatureLayer_management(metro_stations, "metro_stations")
        popul_points_lyr = arcpy.MakeFeatureLayer_management(popul_points, "popul_points")
        districts_lyr = arcpy.MakeFeatureLayer_management(districts, "districts")

        SA = arcpy.CreateFeatureclass_management(r'Z:\Documents\Network_an\Diplom\local_access.gdb', 'SA', "POINT")
        SAlyr = arcpy.MakeFeatureLayer_management(SA, "SA")

        # Network
        arcpy.AddMessage('Start network')
        arcpy.MakeServiceAreaLayer_na(in_network_dataset=network_dataset, out_network_analysis_layer="Service Area5",
                                      impedance_attribute="Minutes", travel_from_to="TRAVEL_FROM",
                                      default_break_values="5 10 15", polygon_type="SIMPLE_POLYS", merge="MERGE",
                                      nesting_type="DISKS", line_type="NO_LINES", overlap="OVERLAP", split="NO_SPLIT",
                                      excluded_source_name="", accumulate_attribute_name="",
                                      UTurn_policy="ALLOW_UTURNS", restriction_attribute_name="",
                                      polygon_trim="TRIM_POLYS", poly_trim_value="500 Meters",
                                      lines_source_fields="NO_LINES_SOURCE_FIELDS", hierarchy="NO_HIERARCHY",
                                      time_of_day="")
        arcpy.AddLocations_na(in_network_analysis_layer="Service Area5", sub_layer="Facilities", in_table=metro_stations_lyr,
                              field_mappings="", search_tolerance="100 Meters", sort_field="",
                              search_criteria="SPrConnections2022 SHAPE;SPrGround2022 SHAPE;SPrMetro2022 SHAPE;feature2022_ND_Junctions NONE",
                              match_type="MATCH_TO_CLOSEST", append="APPEND", snap_to_position_along_network="NO_SNAP",
                              snap_offset="5 Meters", exclude_restricted_elements="INCLUDE",
                              search_query="SPrConnections2022 #;SPrGround2022 #;SPrMetro2022 #;feature2022_ND_Junctions #")
        arcpy.na.GenerateServiceAreas(metro_stations_lyr, "5 10 15", "Minutes", network_dataset, SAlyr)
        arcpy.na.Solve("Service Area5")

        arcpy.AddMessage('Finish network')

        arcpy.FeatureClassToFeatureClass_conversion(in_features="Service Area\Polygons",
                                                    out_path="Z:/Documents/Network_an/Diplom/local_access.gdb",
                                                    out_name="poly_mins", where_clause="",
                                                    field_mapping='FacilityID "FacilityID" true true true 4 Long 0 0 ,First,#,Service Area\Polygons,FacilityID,-1,-1;Name "Name" true true true 1024 Text 0 0 ,First,#,Service Area\Polygons,Name,-1,-1;FromBreak "FromBreak" true true true 8 Double 0 0 ,First,#,Service Area\Polygons,FromBreak,-1,-1;ToBreak "ToBreak" true true true 8 Double 0 0 ,First,#,Service Area\Polygons,ToBreak,-1,-1',
                                                    config_keyword="")
        poly_mins_lyr = arcpy.MakeFeatureLayer_management("Z:/Documents/Network_an/Diplom/local_access.gdb/poly_mins",
                                                          "poly_mins")
        # Cursor
        arcpy.AddMessage('Start cursor')
        fld = ['ToBreak']
        with arcpy.da.SearchCursor(poly_mins_lyr, fld) as cursor:
            for row in cursor:
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="poly_mins_lyr", selection_type="NEW_SELECTION",
                                                        where_clause="ToBreak = {0}".format(row[0]))
                arcpy.CreateFeatureclass_management(r'Z:\Documents\Network_an\Diplom\local_access.gdb', 'SA{0}'.format(row[0]),
                                                         "POINT")
                arcpy.SelectLayerByAttribute_management(in_layer_or_view="poly_mins_lyr", selection_type="CLEAR_SELECTION")

        arcpy.AddMessage('Finish cursor')

        SA5 = r'Z:\Documents\Network_an\Diplom\local_access.gdb\SA5'
        SA10 = r'Z:\Documents\Network_an\Diplom\local_access.gdb\SA10'
        SA15 = r'Z:\Documents\Network_an\Diplom\local_access.gdb\SA15'
        SA5lyr = arcpy.MakeFeatureLayer_management(SA5, "SA5")
        SA15lyr = arcpy.MakeFeatureLayer_management(SA15, "SA15")
        SA10lyr = arcpy.MakeFeatureLayer_management(SA10, "SA10")

        arcpy.AddMessage('Start intersect')
        # Intersect 5
        pre_points_5 = arcpy.CreateFeatureclass_management(r'Z:\Documents\Network_an\Diplom\local_access.gdb', 'pre_points_5',
                                                            "POINT")
        pre_points_5_lyr = arcpy.MakeFeatureLayer_management(pre_points_5, "pre_points_5")
        arcpy.Intersect_analysis([popul_points_lyr, SA5lyr], pre_points_5_lyr, "ALL", "", "point")

        # Intersect 10
        pre_points_10 = arcpy.CreateFeatureclass_management(r'Z:\Documents\Network_an\Diplom\local_access.gdb', 'pre_points_10',
                                                            "POINT")
        arcpy.AddMessage('Middle intersect')
        pre_points_10_lyr = arcpy.MakeFeatureLayer_management(pre_points_10, "pre_points_10")
        arcpy.Intersect_analysis([popul_points_lyr, SA10lyr], pre_points_10_lyr, "ALL", "", "point")

        # Intersect 15
        pre_points_15 = arcpy.CreateFeatureclass_management(r'Z:\Documents\Network_an\Diplom\local_access.gdb', 'pre_points_15',
                                                            "POINT")
        pre_points_15_lyr = arcpy.MakeFeatureLayer_management(pre_points_15, "pre_points_15")
        arcpy.Intersect_analysis([popul_points_lyr, SA15lyr], pre_points_15_lyr, "ALL", "", "point")

        arcpy.AddMessage('Finish intersect')

        # Create temporary points
        points_5 = arcpy.CreateFeatureclass_management(r'Z:\Documents\Network_an\Diplom\local_access.gdb', 'points_5',
                                            'MULTIPOINT',
                                            spatial_reference="Z:\Documents\Network_an\Diplom\Common_access.gdb\center_point")
        points_10 = arcpy.CreateFeatureclass_management(r'Z:\Documents\Network_an\Diplom\local_access.gdb', 'points_10',
                                            'MULTIPOINT',
                                            spatial_reference="Z:\Documents\Network_an\Diplom\Common_access.gdb\center_point")
        points_15 = arcpy.CreateFeatureclass_management(r'Z:\Documents\Network_an\Diplom\local_access.gdb', 'points_15',
                                            'MULTIPOINT',
                                            spatial_reference="Z:\Documents\Network_an\Diplom\Common_access.gdb\center_point")
        arcpy.AddMessage('Finish temporary points')
        # Dissolve_5
        arcpy.Dissolve_management(in_features=pre_points_5_lyr,
                                  out_feature_class=points_5,
                                  dissolve_field="OKATO_2", statistics_fields="Point_popul SUM",
                                  multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
        # Dissolve_10
        arcpy.Dissolve_management(in_features=pre_points_10,
                                  out_feature_class=points_10,
                                  dissolve_field="OKATO_2", statistics_fields="Point_popul SUM",
                                  multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
        # Dissolve_15
        arcpy.Dissolve_management(in_features=pre_points_15,
                                  out_feature_class=points_15,
                                  dissolve_field="OKATO_2", statistics_fields="Point_popul SUM",
                                  multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")

        arcpy.AddMessage('Finish dissolve')

        # Copying tables
        table_5 = arcpy.TableToGeodatabase_conversion(Input_Table="points_5",
                                            Output_Geodatabase="Z:/Documents/Network_an/Diplom/local_access.gdb")
        table_10 = arcpy.TableToGeodatabase_conversion(Input_Table="points_10",
                                            Output_Geodatabase="Z:/Documents/Network_an/Diplom/local_access.gdb")
        table_15 = arcpy.TableToGeodatabase_conversion(Input_Table="points_15",
                                            Output_Geodatabase="Z:/Documents/Network_an/Diplom/local_access.gdb")

        arcpy.AddMessage('Finish copying tables')

        # Create predistricts files
        predistr5 = arcpy.FeatureClassToFeatureClass_conversion(districts_lyr, r'Z:\Documents\Network_an\Diplom\local_access.gdb',
                                                    out_name="predistr5")
        predistr5_lyr = arcpy.MakeFeatureLayer_management(predistr5, "predistr5")
        predistr10 = arcpy.FeatureClassToFeatureClass_conversion(districts_lyr,
                                                                r'Z:\Documents\Network_an\Diplom\local_access.gdb',
                                                                out_name="predistr10")
        predistr10_lyr = arcpy.MakeFeatureLayer_management(predistr10, "predistr10")
        predistr15 = arcpy.FeatureClassToFeatureClass_conversion(districts_lyr,
                                                                r'Z:\Documents\Network_an\Diplom\local_access.gdb',
                                                                out_name="predistr15")
        predistr15_lyr = arcpy.MakeFeatureLayer_management(predistr15, "predistr15")

        arcpy.AddMessage('Finish predistricts')
        # Create new field
        arcpy.AddField_management(in_table="predistr5_lyr", field_name="Proportion", field_type="FLOAT",
                                  field_precision="", field_scale="", field_length="", field_alias="",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
        arcpy.AddField_management(in_table="predistr10_lyr", field_name="Proportion", field_type="FLOAT",
                                  field_precision="", field_scale="", field_length="", field_alias="",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")
        arcpy.AddField_management(in_table="predistr15_lyr", field_name="Proportion", field_type="FLOAT",
                                  field_precision="", field_scale="", field_length="", field_alias="",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

        arcpy.AddMessage('Finish new field')

        # Join field
        arcpy.JoinField_management(in_data="districts_lyr", in_field="OKATO_1", join_table="table_5",
                                   join_field="OKATO_2", fields="SUM_Point_popul")
        arcpy.JoinField_management(in_data="districts_lyr", in_field="OKATO_1", join_table="table_10",
                                   join_field="OKATO_2", fields="SUM_Point_popul")
        arcpy.JoinField_management(in_data="districts_lyr", in_field="OKATO_1", join_table="table_15",
                                   join_field="OKATO_2", fields="SUM_Point_popul")

        arcpy.AddMessage('Finish join')

        # Calculate field
        arcpy.CalculateField_management(in_table="predistr5_lyr", field="Proportion",
                                        expression="[Population] / [SUM_Point_popul]", expression_type="VB", code_block="")
        arcpy.CalculateField_management(in_table="predistr10_lyr", field="Proportion",
                                        expression="[Population] / [SUM_Point_popul]", expression_type="VB",
                                        code_block="")
        arcpy.CalculateField_management(in_table="predistr15_lyr", field="Proportion",
                                        expression="[Population] / [SUM_Point_popul]", expression_type="VB",
                                        code_block="")

        arcpy.AddMessage('Finish calculate field')

        # Generate output
        arcpy.FeatureClassToFeatureClass_conversion(predistr5_lyr, 'populated_area5', populated_area5)
        arcpy.FeatureClassToFeatureClass_conversion(predistr10_lyr, 'populated_area10', populated_area10)
        arcpy.FeatureClassToFeatureClass_conversion(predistr15_lyr, 'populated_area15', populated_area15)

class Walking_access(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Walking_access"
        self.description = "Walking_access"
        self.canRunInBackground = True
    def getParameterInfo(self):
        """Define parameter definitions"""
        metro_stations = arcpy.Parameter(
            displayName="Input metro stations",
            name="metro_stations",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        network_dataset = arcpy.Parameter(
            displayName="Input Network Dataset",
            name="network_dataset",
            datatype="DENetworkDataset",
            parameterType="Required",
            direction="Input")

        popul_points = arcpy.Parameter(
            displayName="Input population points",
            name="popul_points",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        districts = arcpy.Parameter(
            displayName="Input municipal districts",
            name="points_30",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        cr_workspace = arcpy.Parameter(
            displayName="Input workspace",
            name="cr_workspace",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input")

        pop_area = arcpy.Parameter(
            displayName="Output populated area",
            name="populated_area5",
            datatype="GPString",
            parameterType="Required",
            direction="Output")

        params = [metro_stations, network_dataset, popul_points, districts, cr_workspace, pop_area]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        metro_stations = parameters[0].valueAsText
        network_dataset = parameters[1].valueAsText
        popul_points = parameters[2].valueAsText
        districts = parameters[3].valueAsText
        cr_workspace = parameters[4].valueAsText
        pop_area = str(parameters[5].valueAsText)

        # Variables
        arcpy.env.overwriteOutput = True
        metro_stations_lyr = arcpy.MakeFeatureLayer_management(metro_stations, "metro_stations")
        popul_points_lyr = arcpy.MakeFeatureLayer_management(popul_points, "popul_points")
        districts_lyr = arcpy.MakeFeatureLayer_management(districts, "districts_lyr")

        # Network
        arcpy.MakeServiceAreaLayer_na(in_network_dataset=network_dataset, out_network_analysis_layer="Service Area",
                                      impedance_attribute="Minutes", travel_from_to="TRAVEL_FROM",
                                      default_break_values="10", polygon_type="SIMPLE_POLYS", merge="MERGE",
                                      nesting_type="DISKS", line_type="NO_LINES", overlap="OVERLAP", split="NO_SPLIT",
                                      excluded_source_name="", accumulate_attribute_name="",
                                      UTurn_policy="ALLOW_UTURNS", restriction_attribute_name="",
                                      polygon_trim="TRIM_POLYS", poly_trim_value="100 Meters",
                                      lines_source_fields="NO_LINES_SOURCE_FIELDS", hierarchy="NO_HIERARCHY",
                                      time_of_day="")
        arcpy.AddLocations_na(in_network_analysis_layer="Service Area", sub_layer="Facilities", in_table=metro_stations_lyr,
                              field_mappings="", search_tolerance="50 Meters", sort_field="",
                              match_type="MATCH_TO_CLOSEST", append="APPEND", snap_to_position_along_network="NO_SNAP",
                              snap_offset="5 Meters", exclude_restricted_elements="INCLUDE")
        arcpy.na.Solve("Service Area")

        arcpy.AddMessage('Finish network')

        arcpy.FeatureClassToFeatureClass_conversion(in_features='Service Area\Polygons',
                                                    out_path=cr_workspace,
                                                    out_name="poly_mins", where_clause="",
                                                    field_mapping='FacilityID "FacilityID" true true true 4 Long 0 0 ,First,#,Service Area\Polygons,FacilityID,-1,-1;Name "Name" true true true 1024 Text 0 0 ,First,#,Service Area\Polygons,Name,-1,-1;FromBreak "FromBreak" true true true 8 Double 0 0 ,First,#,Service Area\Polygons,FromBreak,-1,-1;ToBreak "ToBreak" true true true 8 Double 0 0 ,First,#,Service Area\Polygons,ToBreak,-1,-1',
                                                    config_keyword="")
        poly_mins_lyr = arcpy.MakeFeatureLayer_management(cr_workspace + "/poly_mins",
                                                          "poly_mins_lyr")


        arcpy.AddMessage('Start intersect')
        # Intersect
        pre_points = arcpy.CreateFeatureclass_management(cr_workspace, 'pre_points',
                                                            "POINT")
        arcpy.Intersect_analysis([popul_points_lyr, poly_mins_lyr], pre_points, "ALL", "", "point")
        pre_points_lyr = arcpy.MakeFeatureLayer_management(pre_points, "pre_points")
        arcpy.AddMessage('Finish intersect')

        # Create temporary points
        prefinish_points = arcpy.CreateFeatureclass_management(cr_workspace, 'prefinish_points',
                                            'MULTIPOINT',
                                            spatial_reference=metro_stations)
        arcpy.AddMessage('Finish temporary points')
        # Dissolve
        arcpy.Dissolve_management(in_features=pre_points,
                                  out_feature_class=prefinish_points,
                                  dissolve_field="OKATO_2", statistics_fields="Point_popul SUM",
                                  multi_part="MULTI_PART", unsplit_lines="DISSOLVE_LINES")
        arcpy.AddMessage('Finish dissolve')
        prefinish_points_lyr = arcpy.MakeFeatureLayer_management(prefinish_points, "prefinish_points")

        # Copying tables
        arcpy.TableToTable_conversion(in_rows="prefinish_points",
                                      out_path=cr_workspace, out_name="table_points")
        arcpy.AddMessage('Finish copying tables')

        # Create predistricts files
        predistr = arcpy.FeatureClassToFeatureClass_conversion(districts_lyr, cr_workspace,
                                                               out_name="predistr")
        predistr_lyr = arcpy.MakeFeatureLayer_management(predistr, "predistr_lyr")
        arcpy.AddMessage('Finish predistricts')
        # Create new field
        arcpy.AddField_management(in_table="predistr_lyr", field_name="Proportion", field_type="FLOAT",
                                  field_precision="", field_scale="", field_length="", field_alias="",
                                  field_is_nullable="NULLABLE", field_is_required="NON_REQUIRED", field_domain="")

        arcpy.AddMessage('Finish new field')

        # Join field
        arcpy.JoinField_management(in_data=predistr_lyr, in_field="OKATO_1", join_table=cr_workspace + "/table_points",
                                   join_field="OKATO_2", fields="SUM_Point_popul")
        arcpy.AddMessage('Finish join')

        # Calculate field
        arcpy.CalculateField_management(in_table="predistr_lyr", field="Proportion",
                                        expression="[SUM_Point_popul] / [Population] *100", expression_type="VB", code_block="")
        arcpy.SelectLayerByAttribute_management(in_layer_or_view="predistr_lyr", selection_type="NEW_SELECTION",
                                                where_clause="Proportion IS NULL")
        arcpy.CalculateField_management(in_table="predistr_lyr", field="Proportion",
                                        expression="0", expression_type="VB",
                                        code_block="")
        arcpy.SelectLayerByAttribute_management(in_layer_or_view="predistr_lyr", selection_type="CLEAR_SELECTION")

        arcpy.AddMessage('Finish calculate field')

        # Generate output
        arcpy.FeatureClassToFeatureClass_conversion(predistr_lyr, cr_workspace, out_name=pop_area)