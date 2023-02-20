from subprocess import call
import math
import time

width = 143 * 2
height = 38 * 2
global frame
frame = [0]*(width*height)

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


vertex = [
 [-1,-1,-1],
 [-1,-1,1],
 [1,-1,1],
 [1,-1,-1],

 [-1,1,-1],
 [-1,1,1],
 [1,1,1],
 [1,1,-1]

 # [-1,-1,-1],
 # [1,0.5,-1],
 # [-1,1,-1],
 # [0.5,0.5,1]
]

def normalize(vec):
  mag = math.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)
  return [vec[0]/mag,vec[1]/mag,vec[2]/mag]
  

normals = []
for i in vertex:
  normals.append(normalize(i))

faces = [
 [0,1,2,  0.55],
 [2,3,0,  0.55],

 [4,5,6,  0.55],
 [6,7,4,  0.55],

 [0,1,4,  0.55],
 [4,5,1,  0.55],

 [2,3,6,  0.55],
 [6,7,3,  0.55],

 [1,2,5,  0.55],
 [5,6,2,  0.55],

 [3,0,7,  0.55],
 [7,4,0,  0.55]

 # [0,1,2, 0.35],

 # [0,2,3, 0.55],

 # [0,1,3, 0.75],

 # [1,2,3, 0.95]

]

def setColor(i):
 val = int(math.ceil(232 + i * (255-232)))
 return "\\e[48;5;"+str(val)+"m"

def lerp(p,A,B):
  r=[A[0]+p*(B[0]-A[0]),
     A[1]+p*(B[1]-A[1]),
     A[2]+p*(B[2]-A[2])]
  return normalize(r)

def dot(a,b):
  return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

def setPixel(x,y,z,n,color):
 global frame
 global depth
 if (y<0 or x<0 or x>width-1 or y>height-1):
  return
 if ( -z > depth[width*y+x] ):
  return
 dL = dot(n,[1,1,1])
 if dL<0:
  dL =0
 light = color*(dL+0.5)
 if light>1:
  light =1
 frame[width*y+x] = light
 depth[width*y+x] = -z

def drawLine(x1,y1,z1,x2,y2,z2,color):
 dx = x2-x1
 dy = y2-y1
 mag = math.sqrt(dx*dx+dy*dy)
 setPixel(int(x1),int(y1),z1,color)
 if (mag==0):
  return
 dx /= mag
 dy /= mag
 for i in range(int(mag)):
  z = float(i+0.5)/mag * (z2-z1) + z1
  setPixel(int(x1),int(y1),z,color)
  x1 += dx
  y1 += dy
 return

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
  nAB = lerp(pAB,A[3],B[3])
  nAC = lerp(pAC,A[3],C[3])
  xL = A[0] + pAB*(B[0]-A[0])
  xR = A[0] + pAC*(C[0]-A[0])
  zB = A[2] + pAB*(B[2]-A[2])
  zC = A[2] + pAC*(C[2]-A[2])
  x = xL
  while x <= xR:
   pBC = float(x-xL)/(xR-xL+0.001)
   nBC = lerp(pBC,nAB,nAC)
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
   nAB = lerp(pAB,A[3],B[3])
   nCB = lerp(pCB,C[3],B[3])
   xL = A[0] + pAB*(B[0]-A[0])
   xR = C[0] + pCB*(B[0]-C[0])
   zA = A[2] + pAB*(B[2]-A[2])
   zC = C[2] + pCB*(B[2]-C[2])
   x = xL
   while x <= xR:
    pAC = float(x-xL)/(xR-xL+0.001)
    nAC = lerp(pAC,nAB,nCB)
    z = zA + pAC*(zC-zA)
    setPixel(int(x),int(y),z,nAC,color)
    x += 1
   y += 1
 else:
  y = B[1]
  while y <= C[1]:
   pBC = float(y-B[1])/(C[1]-B[1]+0.001)
   pAC = float(y-A[1])/(C[1]-A[1]+0.001)
   nBC = lerp(pBC,B[3],C[3])
   nAC = lerp(pAC,A[3],C[3])
   xL = B[0] + pBC*(C[0]-B[0])
   xR = A[0] + pAC*(C[0]-A[0])
   zA = A[2] + pAC*(C[2]-A[2])
   zB = B[2] + pBC*(C[2]-B[2])
   x = xL
   while x <= xR:
    pBA = float(x-xL)/(xR-xL+0.001)
    nBA = lerp(pBA,nBC,nAC)
    z = zB + pBA*(zA - zB)
    setPixel(int(x),int(y),z,nBA,color)
    x += 1
   y += 1
 return
 

def modelview(vec3,view):
 CENTER = view['center']
 ROT = view['rotation']
 SCALE = view['scale']
 angle = ROT[0]
 angle2 = ROT[1]
 pos = [math.cos(angle)*vec3[0] - math.sin(angle)*vec3[2],
        vec3[1],
        math.sin(angle)*vec3[0] + math.cos(angle)*vec3[2]]

 pos = [math.cos(angle2)*pos[0] - math.sin(angle2)*pos[1],
        math.sin(angle2)*pos[0] + math.cos(angle2)*pos[1],
        pos[2]]
 pos[0] *= SCALE[0]
 pos[1] *= SCALE[1]
 pos[2] *= SCALE[2]
 pos[0] += CENTER[0]
 pos[1] += CENTER[1]
 pos[2] += CENTER[2]
 return pos
   

def project(vec3,TIME):
 angle = TIME
 FoV = 18
 alpha = 0.5
 camZ = -4
 camX = 0
 camY = 0
 x = (vec3[0]+camX)/(vec3[2]*alpha+camZ) * FoV * 3.5 + width/2
 y = (vec3[1]+camY)/(vec3[2]*alpha+camZ) * FoV * 1.5 + height/2
 z = vec3[2]
 return [x,y,z]

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


 frame = [0]*(width*height)
 depth = [1000]*(width*height)

 TIME = time.time()

 xP += xDir *.05
 yP += yDir *.05
 zP += zDir *.05

 if xP>7 or xP<-7:
  xDir *=-1
 if yP>3 or yP<-3:
  yDir *= -1
 if zP>4 or zP<-8:
  zDir *= -1

 Views = [
  { 'center': [xP,yP,zP-5],
    'rotation': [TIME,TIME*0.5],
    'scale': [2,2,2] },
  # { 'center': [-xP,-yP,-zP-5],
  #   'rotation': [-TIME,-TIME/3],
  #   'scale': [1.6,1,1.6] }
 ]

 color = 1
 for View in Views:
  for face in faces:
   mv1 = modelview(vertex[face[0]],View)
   mv2 = modelview(vertex[face[1]],View)
   mv3 = modelview(vertex[face[2]],View)
   Norm = {
     'center': [0,0,0],
     'rotation': View['rotation'],
     'scale': [1,1,1]
   }
   n1 = modelview(normals[face[0]],Norm)
   n2 = modelview(normals[face[1]],Norm)
   n3 = modelview(normals[face[2]],Norm)
   pt1 = project(mv1,TIME)
   pt2 = project(mv2,TIME)
   pt3 = project(mv3,TIME)
   color = face[3]
   fillTriangle(
    [pt1[0],pt1[1],pt1[2],n1],
    [pt2[0],pt2[1],pt2[2],n2],
    [pt3[0],pt3[1],pt3[2],n3],color)
   # drawLine(pt1[0],pt1[1],pt1[2],pt2[0],pt2[1],pt2[2],color)
   # drawLine(pt2[0],pt2[1],pt2[2],pt3[0],pt3[1],pt3[2],color)
   # drawLine(pt3[0],pt3[1],pt3[2],pt1[0],pt1[1],pt1[2],color)

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
