"""Provides a scripting component.
    Inputs:
        m: a mesh
        s: sun vector
    Output:
        a: List of Vectors
        b: List of Points
        c: list of angles
        d: exploded mesh
        """

#mesh needed to be flipped for correct vector direction

m.Flip(m,True,True)

import Rhino.Geometry as rg
import ghpythonlib.treehelpers as th
import math
import rhinoscriptsyntax as rs
import Rhino.Geometry.Collections as rgc


#1.
#compute face normals using rg.Mesh.FaceNormals.ComputeFaceNormals()
#output the vectors to a

m.FaceNormals.ComputeFaceNormals()

a = m.FaceNormals

#2.
#get the centers of each faces using rg.Mesh.Faces.GetFaceCenter()
#store the centers into a list called centers 
#output that list to b

centers = []
for i in range(len(m.Faces)):
    center = m.Faces.GetFaceCenter(i)
    centers.append(center)

b = centers

#3.
#calculate the angle between the sun and each FaceNormal using rg.Vector3d.VectorAngle()
#store the angles in a list called angleList and output it to c

angleList=[]
for j in a:
    angle = rg.Vector3d.VectorAngle(j, s)
    angleList.append(angle)

c = angleList

#4. explode the mesh - convert each face of the mesh into a mesh
#for this, you have to first copy the mesh using rg.Mesh.Duplicate()
#then iterate through each face of the copy, extract it using rg.Mesh.ExtractFaces
#and store the result into a list called exploded in output d

exploded=[]
numesh=m.Duplicate()
nufaces=numesh.Faces
for k in range(len(nufaces)):
     explo=nufaces.ExtractFaces([0])
     exploded.append(explo)

d = exploded

#after here, your task is to apply a transformation to each face of the mesh
#the transformation should correspond to the angle value that corresponds that face to it... 
#the result should be a mesh that responds to the sun position... its up to you!

circles=[]
d_outlines=[]
moved_circles=[]
# offsetcurve=[]
# extrusion=[]
NL=[]
for k in range(len(d)):
    pl=rg.Plane(b[k], a[k])
    # out=rg.Mesh.GetOutlines(d[k], pl)[0]
    out=rg.Mesh.GetNakedEdges(d[k])
    for l in range(len(out)):
        m_line=out[l]
        linesss=m_line.ToNurbsCurve()
        NL.append(linesss)
    NB=rg.Curve.JoinCurves(NL)[0]
    d_outlines.append(NB)
    circ=rg.Circle(pl, 0.05*c[k])
    circ_nurb=rg.Circle.ToNurbsCurve(circ, 2, 5)
    rg.Curve.Transform(circ_nurb, rg.Transform.Translation(a[k]))
    circles.append(circ)
    moved_circles.append(circ_nurb)

circ=circles
joined_outlines=d_outlines

#remap angleList
remapped=[]
for i in angleList:
    remapped_value=(((i - min(angleList)) * (max_off - min_off)) / (max(angleList) - min(angleList))) + min_off
    remapped.append(remapped_value)

#Get the Faces outlines
outlines = []
for i in exploded:
    outline = rg.Mesh.GetNakedEdges(i)
    outlines.append(outline)

# outlines=th.list_to_tree(outlines)

#join outlines
joined_outlines=[]
for i in outlines:
    curves=[]
    for j in i:
        curve=rg.Polyline.ToNurbsCurve(j)
        curves.append(curve)
    joined=rg.Curve.JoinCurves(curves)[0]
    joined_outlines.append(joined)

#Offset outlines
#get 4 points off the mesh and draw surface from them
mesh_points=[]
for i in exploded:
    points=rg.Mesh.Vertices.GetValue(i) #this line and i.Vertices is the same thing
    # points=i.Vertices
    mesh_points.append(points)
mesh_points_3d=[]
for i in mesh_points:
    sub=[]
    for j in i:
        pt=rg.Point3d(j)
        sub.append(pt)
    mesh_points_3d.append(sub)
    
#mesh_points_3d=th.list_to_tree(mesh_points_3d)

#Create Nurbs Surface
surfaces=[]
offset_outlines=[]
for i in range(len(joined_outlines)):
    surface=rg.NurbsSurface.CreateFromPoints(mesh_points_3d[i],2,2,2,2)
    off=rg.Curve.OffsetOnSurface(joined_outlines[i],surface,remapped[i],.001)[0]
    offset_outlines.append(off)
    surfaces.append(surface)


#Loft
lofted_breps=[]
for i in range(len(offset_outlines)):
     list_curves=[offset_outlines[i],joined_outlines[i]]
     lofted=rg.Brep.CreateFromLoft(list_curves, rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)[0]
     lofted_breps.append(lofted)

#Loft circle and inner frame
lofted_cones=[]
for i in range(len(offset_outlines)):
    t_p=rg.Curve.ClosestPoint(moved_circles[i],rg.Curve.PointAt(offset_outlines[i],0),5)[1]
    rg.Curve.ChangeClosedCurveSeam(moved_circles[i],t_p)
    list_curves2=[offset_outlines[i], moved_circles[i]]
    lofted_circs=rg.Brep.CreateFromLoft(list_curves2, rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)[0]
    lofted_cones.append(lofted_circs)



########################################## BONUS EXERCISE
#get vertex normals
mesh_copy=m.Duplicate()
Vertex_normal_list=rg.Mesh.Normals.GetValue(mesh_copy) #this gives mesh vertices normals
# rgc.MeshVertexNormalList.ComputeNormals(Vertex_normal_list)
e=Vertex_normal_list
vert=mesh_copy.Vertices

#Move vertices 
#moved_vertex=[]
#for i in range(len(Vertex_normal_list)):
#    pt=rg.Point3d(vert[i])
#    vector=rg.Vector3d.Multiply((vec_length/abs(Vertex_normal_list[i].Length)), Vertex_normal_list[i])
#    rg.Point3d.Transform(pt, rg.Transform.Translation(vector))
#    moved_vertex.append(pt)

# Sort points
list_1=[]
for i in range(0, len(vert), V+1):
    sub_list=[]
    for j in range(V+1):
        pt=rg.Point3d(vert[i+j])
        sub_list.append(pt)
        # pt=vert[i][j]
    # sub_list.append(pt)
    list_1.append(sub_list)
# moved_vertex=th.list_to_tree(list_1)
list_11=th.list_to_tree(list_1)

list_2=[]
#sort in other direction
for i in range(0,V+1):
    sub=[]
    for j in range(U+1):
        pt=rg.Point3d(vert[i+j+(j*V)])
        sub.append(pt)
    list_2.append(sub)
    

list_22=th.list_to_tree(list_2)

######
# Draw Polylines
polylines_1=[]
for i in list_1:
    poly=rg.Polyline(i)
    polylines_1.append(poly)
polylines_2=[]
for i in list_2:
    poly=rg.Polyline(i)
    polylines_2.append(poly)
    
T_Parameters_1=[]
for i in range(len(list_1)):
    sub=[]
    for j in range(len(list_1[i])):
        
        curve=rg.Polyline.ToNurbsCurve(polylines_1[i])
        t_p=rg.Curve.ClosestPoint(curve, list_1[i][j],.1)[1]
        sub.append(t_p)
    T_Parameters_1.append(sub)

T_Parameters_2=[]
for i in range(len(list_2)):
    sub=[]
    for j in range(len(list_2[i])):
        
        curve=rg.Polyline.ToNurbsCurve(polylines_2[i])
        t_p=rg.Curve.ClosestPoint(curve, list_2[i][j],.1)[1]
        sub.append(t_p)
    T_Parameters_2.append(sub)


##########

tangents_1=[]
points_1=[]
for i in range(len(polylines_1)):
    sub=[]
    sub_pt=[]
    for j in range(V+1):
        curve=rg.Polyline.ToNurbsCurve(polylines_1[i])
        pt=rg.Curve.PointAt(curve,T_Parameters_1[i][j])
        tan=rg.NurbsCurve.TangentAt(curve,T_Parameters_1[i][j])
        sub.append(tan)
        sub_pt.append(pt)
    points_1.append(sub_pt)
    tangents_1.append(sub)
#points_1=th.list_to_tree(points_1)

tangents_2=[]
points_2=[]
for i in range(len(polylines_2)):
    sub=[]
    sub_pt=[]
    for j in range(U+1):
        curve=rg.Polyline.ToNurbsCurve(polylines_2[i])
        pt=rg.Curve.PointAt(curve,T_Parameters_2[i][j])
        tan=rg.NurbsCurve.TangentAt(curve,T_Parameters_2[i][j])
        sub.append(tan)
        sub_pt.append(pt)
    points_2.append(sub_pt)
    tangents_2.append(sub)
#points_2=th.list_to_tree(points_2)


#Graft_normal_list_2
Grafted_normals_2=[]
for i in range(V+1):
    sub=[]
    for j in range(U+1):
        grafted=Vertex_normal_list[i+(j*V)+j]
#        grafted=rg.Vector3d(grafted)
        sub.append(grafted)
    Grafted_normals_2.append(sub)
cc=th.list_to_tree(Grafted_normals_2)


#############
#Graft_normal_list_1
Grafted_normals_1=[]
for i in range(0,len(vert),V+1):
    sub_list=[]
    for j in range(V+1):
        grafted=Vertex_normal_list[i+j]
        grafted=rg.Vector3d(grafted) #to avoid the problem of vector3f
        sub_list.append(grafted)
    Grafted_normals_1.append(sub_list)
dd=th.list_to_tree(Grafted_normals_1)

#get the cross product OF THE VECTORS

cross_vector_1=[]
cross_vector_2=[]
for i in range(len(Grafted_normals_1)):
    sub_1=[]
    for j in range(len(Grafted_normals_1[i])):
        cross_v_1=rg.Vector3d.CrossProduct(Grafted_normals_1[i][j],tangents_1[i][j])
        sub_1.append(cross_v_1)
    cross_vector_1.append(sub_1)
        
for i in range(len(Grafted_normals_2)):
    sub_2=[]
    for j in range(len(Grafted_normals_2[i])):
        cross_v_2=rg.Vector3d.CrossProduct(Grafted_normals_2[i][j],tangents_2[i][j])
        sub_2.append(cross_v_2)
    cross_vector_2.append(sub_2)
vectors_1=th.list_to_tree(cross_vector_1)
vectors_2=th.list_to_tree(cross_vector_2)

####### GET PLANES

planes_1=[]
for i in range(len(Grafted_normals_1)):
    sub=[]
    for j in range(len(Grafted_normals_1[i])):
        plane_1=rg.Plane(points_1[i][j], Grafted_normals_1[i][j],cross_vector_1[i][j])
        sub.append(plane_1)
    planes_1.append(sub)
    
planes_2=[]
for i in range(len(Grafted_normals_2)):
    sub=[]
    for j in range(len(Grafted_normals_2[i])):
        plane_2=rg.Plane(points_2[i][j], Grafted_normals_2[i][j],cross_vector_2[i][j])
        sub.append(plane_2)
    planes_2.append(sub)
#planes_1=th.list_to_tree(planes_1)
#planes_2=th.list_to_tree(planes_2)

#Draw rectangles
rectangles_1=[]
for i in range(len(planes_1)):
    sub=[]
    for j in range(len(planes_1[i])):
        rec=rg.Rectangle3d(planes_1[i][j], height, width)
        sub.append(rec)
    rectangles_1.append(sub)

rectangles_2=[]
for i in range(len(planes_2)):
    sub=[]
    for j in range(len(planes_2[i])):
        rec=rg.Rectangle3d(planes_2[i][j], height, width)
        sub.append(rec)
    rectangles_2.append(sub)

#rectangles_1=th.list_to_tree(rectangles_1)
#rectangles_2=th.list_to_tree(rectangles_2)

#MOVE THE RECTANGLES

cross_sections_1=[]
for i in range(len(rectangles_1)):
    sub=[]
    for j in range(len(rectangles_1[i])):
        vect1=rg.Vector3d.Multiply((-height/2)/abs(Grafted_normals_1[i][j].Length), Grafted_normals_1[i][j])
        vect2=rg.Vector3d.Multiply((-width/2)/abs(cross_vector_1[i][j].Length), cross_vector_1[i][j])
        rg.Rectangle3d.Transform(rectangles_1[i][j], rg.Transform.Translation(vect1))
        rg.Rectangle3d.Transform(rectangles_1[i][j],rg.Transform.Translation(vect2))
        rec=rg.Rectangle3d.ToNurbsCurve(rectangles_1[i][j])
        sub.append(rec)
    cross_sections_1.append(sub)

cross_sections_2=[]
for i in range(len(rectangles_2)):
    sub=[]
    for j in range(len(rectangles_2[i])):
        vect1=rg.Vector3d.Multiply((-height/2)/abs(Grafted_normals_2[i][j].Length), Grafted_normals_2[i][j])
        vect2=rg.Vector3d.Multiply((-width/2)/abs(cross_vector_2[i][j].Length), cross_vector_2[i][j])
        rg.Rectangle3d.Transform(rectangles_2[i][j], rg.Transform.Translation(vect1))
        rg.Rectangle3d.Transform(rectangles_2[i][j],rg.Transform.Translation(vect2))
        rec=rg.Rectangle3d.ToNurbsCurve(rectangles_2[i][j])
        sub.append(rec)
    cross_sections_2.append(sub)

#cross_sections_2=th.list_to_tree(cross_sections_2)
#cross_sections_1=th.list_to_tree(cross_sections_1)

#Loft
beams_1=[]
for i in cross_sections_1:
    beam=rg.Brep.CreateFromLoft(i, rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)[0]
    beams_1.append(beam)

beams_2=[]
for i in cross_sections_2:
    beam=rg.Brep.CreateFromLoft(i, rg.Point3d.Unset, rg.Point3d.Unset, rg.LoftType.Normal, False)[0]
    beams_2.append(beam)