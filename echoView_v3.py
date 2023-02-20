from subprocess import call
import math
import time
import argparse

parser = argparse.ArgumentParser("EchoView")
parser.add_argument("file", help="Object file to load in terminal", type=str)
args = parser.parse_args()

width = 143 * 2
height = 38 * 2
global frame
frame = [0]*(width*height)

global TIME
TIME = time.time()

global depth
depth = [1000]*(width*height)

global xDir
xDir = 1

global yDir
yDir = 1

global zDir
zDir = 1

global xP
xP = 0

global yP
yP = 0

global zP
zP = 0

obj = args.file

vertex = []

f = open(obj)

for line in f:
  a = line.split()
  if len(a)>0:
    if a[0] == 'v':
      b = a[1:4]
      for i in range(len(b)):
        b[i] = float(b[i])
      vertex.append(b)

f.close()

def normalize(vec):
  mag = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
  return [vec[0]/mag,vec[1]/mag,vec[2]/mag]
  

normals = []
# for i in vertex:
#   normals.append(normalize(i))

f = open(obj)

for line in f:
  a = line.split()
  if len(a)>0:
    if a[0] == 'vn':
      b = a[1:4]
      for i in range(len(b)):
        b[i] = float(b[i])
      normals.append(b)

f.close()


faces = []

f = open(obj)

for line in f:
  params = line.split()
  if len(params)>0:
    if params[0][0] == 'f':
      vertices = params[1:]
      face = []
      for V in vertices:
        components = V.split('/')
        positionIdx = int(components[0])
        texCoordIdx = 0#int(components[1])
        normalIdx   = int(components[2])
        face.append([positionIdx, texCoordIdx, normalIdx])
      faces.append(face)


f.close()

print("NUMBER OF FACES: " + str(len(faces)))

def setColor(i):
 val = int(math.ceil(232 + i * (255-232)))
 return "\\e[48;5;"+str(val)+"m"

## linear interpolation (from A to B, percentage p)
def lerp(p,A,B): 
  r=[A[0]+p*(B[0]-A[0]),
     A[1]+p*(B[1]-A[1]),
     A[2]+p*(B[2]-A[2])]
  return r

## dot product of 3vector a and b
def dot(a,b):
  return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

## This method behaves like a fragment shader program
## set the fragment color at location x,y with depth z and normal n
def setPixel(x,y,z,n,color):
 global frame
 global depth
 global TIME
 if (y<0 or x<0 or x>width-1 or y>height-1):
  return
 if ( -z > depth[width*y+x] ):
  return
 AMBIENT = 0.2
 DIFFUSE = 0.7
 SPECULAR = 4.5
 GLOSSINESS = 15
 L = normalize([1,1,1])
 dL = dot(n,L)
 ## Reflected ray = I + 2*(N.I)*N
 I = [0, 0, 1]
 dotNI = dot(n, I)
 R = [2*(dotNI)*n[0] + I[0],
      2*(dotNI)*n[1] + I[1],
      2*(dotNI)*n[2] + I[2]]
 dS = dot(normalize(R), L)
 if (dS < 0):
  dS = 0
 dS = dS**(GLOSSINESS)
 if dL<0:
  dL =0
 light = color*(dS*dL*SPECULAR + dL*DIFFUSE + AMBIENT)
 if light>1:
  light = 1
 frame[width*y+x] = light
 depth[width*y+x] = -z

## given three 3vectors (acting as coordinates), draw a triangle
## filled in by a given color.
##
## Given points A, B, and C.  The filling process is split in to
## a few steps. First, the boundary coordinates are sorted from
## leftmost x to rightmost x (smallest to largest).  Then the actual
## filling step is accomplished in two phases.  The following diagram
## illustrates the inputs and filling process.
##
## INPUT:
##            A
## 
##
##    B           
##                 
##                  C
##
## SORTED BY X:
##            B
## 
##
##    A           
##                 
##                  C
##
## FILL STEPS (1 and 2):
##           1B
##        111112
##      111111122
##    A111111112222           
##          11122222       
##               222C
##
def fillTriangle(pt1,pt2,pt3,color):
 A = pt1
 B = pt2
 C = pt3
 if ( pt2[0] > pt3[0] ):
  B = pt3
  C = pt2
 if ( pt2[1]< pt1[1] and pt2[1] < pt3[1] ):
  A = pt2
  if ( pt1[0] > pt3[0] ):
   B = pt3
   C = pt1
  else:
   B = pt1
   C = pt3
 elif ( pt3[1] < pt1[1] and pt3[1] < pt2[1]):
  A = pt3
  if ( pt1[0] > pt2[0] ):
   B = pt2
   C = pt1
  else:
   B = pt1
   C = pt2

 ACx = C[0]-A[0]
 ACy = C[1]-A[1]
 ABx = B[0]-A[0]
 ABy = B[1]-A[1]
 if ( ABx*ACy - ABy*ACx > 0  ):
  T = B
  B = C
  C = T

 xL = A[0]
 xR = A[0]
 y = A[1]
 yMax = B[1]
 if ( C[1] < yMax ):
  yMax = C[1]
 while y <= yMax:
  pAB = float(y-A[1])/(B[1]-A[1]+0.001)
  pAC = float(y-A[1])/(C[1]-A[1]+0.001)
  nAB = normalize(lerp(pAB,A[3],B[3]))
  nAC = normalize(lerp(pAC,A[3],C[3]))
  xL = A[0] + pAB*(B[0]-A[0])
  xR = A[0] + pAC*(C[0]-A[0])
  zB = A[2] + pAB*(B[2]-A[2])
  zC = A[2] + pAC*(C[2]-A[2])
  x = xL
  while x <= xR:
   pBC = float(x-xL)/(xR-xL+0.001)
   nBC = normalize(lerp(pBC,nAB,nAC))
   z = zB + pBC*(zC-zB)
   setPixel(int(x),int(y),z,nBC,color)
   x += 1
  y+=1

 #other half
 if ( C[1] < B[1] ):
  y = C[1]
  while y <= B[1]:
   pAB = float(y-A[1])/(B[1]-A[1]+0.001)
   pCB = float(y-C[1])/(B[1]-C[1]+0.001)
   nAB = normalize(lerp(pAB,A[3],B[3]))
   nCB = normalize(lerp(pCB,C[3],B[3]))
   xL = A[0] + pAB*(B[0]-A[0])
   xR = C[0] + pCB*(B[0]-C[0])
   zA = A[2] + pAB*(B[2]-A[2])
   zC = C[2] + pCB*(B[2]-C[2])
   x = xL
   while x <= xR:
    pAC = float(x-xL)/(xR-xL+0.001)
    nAC = normalize(lerp(pAC,nAB,nCB))
    z = zA + pAC*(zC-zA)
    setPixel(int(x),int(y),z,nAC,color)
    x += 1
   y += 1
 else:
  y = B[1]
  while y <= C[1]:
   pBC = float(y-B[1])/(C[1]-B[1]+0.001)
   pAC = float(y-A[1])/(C[1]-A[1]+0.001)
   nBC = normalize(lerp(pBC,B[3],C[3]))
   nAC = normalize(lerp(pAC,A[3],C[3]))
   xL = B[0] + pBC*(C[0]-B[0])
   xR = A[0] + pAC*(C[0]-A[0])
   zA = A[2] + pAC*(C[2]-A[2])
   zB = B[2] + pBC*(C[2]-B[2])
   x = xL
   while x <= xR:
    pBA = float(x-xL)/(xR-xL+0.001)
    nBA = normalize(lerp(pBA,nBC,nAC))
    z = zB + pBA*(zA - zB)
    setPixel(int(x),int(y),z,nBA,color)
    x += 1
   y += 1
 return
 

## transform a single 3vector given a view "matrix"
def modelview(vec3,view):
 CENTER = view['center']
 ROT = view['rotation']
 SCALE = view['scale']
 angle = ROT[0]
 angle2 = ROT[1]
 angle3 = ROT[2]
 pos = [math.cos(angle)*vec3[0] - math.sin(angle)*vec3[2],
        vec3[1],
        math.sin(angle)*vec3[0] + math.cos(angle)*vec3[2]]

 pos = [math.cos(angle2)*pos[0] - math.sin(angle2)*pos[1],
        math.sin(angle2)*pos[0] + math.cos(angle2)*pos[1],
        pos[2]]

 pos = [pos[0],
        math.cos(angle3)*pos[1] - math.sin(angle3)*pos[2],
        math.sin(angle3)*pos[1] + math.cos(angle3)*pos[2]]

 pos[0] *= SCALE[0]
 pos[1] *= SCALE[1]
 pos[2] *= SCALE[2]
 pos[0] += CENTER[0]
 pos[1] += CENTER[1]
 pos[2] += CENTER[2]
 return pos
   
## project a 3vector coordinate to the screen (3D world to 2D projection)
def project(vec3):
 FoV = 18
 alpha = 0.5
 camZ = -4
 camX = 0
 camY = 0
 x = (vec3[0]+camX)/(vec3[2]*alpha+camZ) * FoV * 3.5 + width/2
 y = (vec3[1]+camY)/(vec3[2]*alpha+camZ) * FoV * 1.5 + height/2
 z = vec3[2]
 return [x,y,z]

## renders all faces of the model while changing the camera position
def update():
 global frame
 global vertex
 global faces
 global depth
 global xP
 global yP
 global zP
 global xDir
 global yDir
 global zDir
 global TIME


 frame = [0]*(width*height)
 depth = [1000]*(width*height)

 TIME = time.time()

 xP += xDir *.1
 yP += yDir *.1
 zP += zDir *.1

 if xP>7 or xP<-7:
  xDir *=-1
 if yP>3 or yP<-3:
  yDir *= -1
 if zP>4 or zP<-4:
  zDir *= -1

 
 # # CAMARO
 Views = [
  { 'center': [4,0,-8],
    'rotation': [TIME*0.3, 0.0, 0.5],#[TIME, 0.3 * TIME],
    'scale': [1.25, 1.25, 1.25] },
  { 'center': [-10,2,-6],
    'rotation': [TIME*0.3, 1.5, 0.5],#[TIME, 0.3 * TIME],
    'scale': [0.5, 0.5, 0.5] }
 ]
 
 
 # HEAD
#  Views = [
#   { 'center': [0,0,-3],
#     'rotation': [TIME, 0.3 * TIME, 0],
#     'scale': [20, 20, 20] }
#  ]

 color = 1
 for View in Views:
  for face in faces:
   mv1 = modelview(vertex[face[0][0]-1],View)
   mv2 = modelview(vertex[face[1][0]-1],View)
   mv3 = modelview(vertex[face[2][0]-1],View)
   Norm = {
     'center': [0,0,0],
     'rotation': View['rotation'],
     'scale': [1,1,1]
   }
   n1 = modelview(normals[face[0][2]-1],Norm)
   n2 = modelview(normals[face[1][2]-1],Norm)
   n3 = modelview(normals[face[2][2]-1],Norm)
   if (dot(n1, [0,0,1]) < 0 and dot(n2, [0,0,1]) < 0 and dot(n3, [0,0,1]) < 0):
    continue
   pt1 = project(mv1)
   pt2 = project(mv2)
   pt3 = project(mv3)
   color = 0.55
   fillTriangle(
    [pt1[0],pt1[1],pt1[2],n1],
    [pt2[0],pt2[1],pt2[2],n2],
    [pt3[0],pt3[1],pt3[2],n3],color)

 return

while True:
 update()
 acc = "\033[0;0f"
 for i in range(width*height):
  if (i)%width == 0:
    acc += '\n'
  if (frame[i]==0):
   acc += " "
  else:
   acc += setColor(frame[i])+ " \\e[0m"

 call(["echo","-e",acc])
