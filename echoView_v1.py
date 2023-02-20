from subprocess import call
import math
import time

width = 143
height = 38

global frame
frame = [0]*(width*height)

global depth
depth = [1000]*(width*height)

vertex = [
 [-1,-1,-1],
 [-1,-1,1],
 [1,-1,1],
 [1,-1,-1],

 [-1,1,-1],
 [-1,1,1],
 [1,1,1],
 [1,1,-1]
]

faces = [
 [0,1,2,  41],
 [2,3,0,  41],

 [4,5,6,  42],
 [6,7,4,  42],

 [0,1,4,  43],
 [4,5,1,  43],

 [2,3,6,  44],
 [6,7,3,  44],

 [1,2,5,  45],
 [5,6,2,  45],

 [3,0,7,  46],
 [7,4,0,  46]
]

def setColor(i):
 return "\\e["+str(i)+"m"

def setPixel(x,y,z,color):
 global frame
 global depth
 if (y<0 or x<0 or x>width-1 or y>height-1):
  return
 if ( -z > depth[width*y+x] ):
  return
 frame[width*y+x] = color
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
  xL = A[0] + pAB*(B[0]-A[0])
  xR = A[0] + pAC*(C[0]-A[0])
  zB = A[2] + pAB*(B[2]-A[2])
  zC = A[2] + pAC*(C[2]-A[2])
  x = xL
  while x <= xR:
   pBC = float(x-xL)/(xR-xL+0.001)
   z = zB + pBC*(zC-zB)
   setPixel(int(x),int(y),z,color)
   x += 1
  y+=1

 #other half
 if ( C[1] < B[1] ):
  y = C[1]
  while y <= B[1]:
   pAB = float(y-A[1])/(B[1]-A[1]+0.001)
   pCB = float(y-C[1])/(B[1]-C[1]+0.001)
   xL = A[0] + pAB*(B[0]-A[0])
   xR = C[0] + pCB*(B[0]-C[0])
   zA = A[2] + pAB*(B[2]-A[2])
   zC = C[2] + pCB*(B[2]-C[2])
   x = xL
   while x <= xR:
    pAC = float(x-xL)/(xR-xL+0.001)
    z = zA + pAC*(zC-zA)
    setPixel(int(x),int(y),z,color)
    x += 1
   y += 1
 else:
  y = B[1]
  while y <= C[1]:
   pBC = float(y-B[1])/(C[1]-B[1]+0.001)
   pAC = float(y-A[1])/(C[1]-A[1]+0.001)
   xL = B[0] + pBC*(C[0]-B[0])
   xR = A[0] + pAC*(C[0]-A[0])
   zA = A[2] + pAC*(C[2]-A[2])
   zB = B[2] + pBC*(C[2]-B[2])
   x = xL
   while x <= xR:
    pBA = float(x-xL)/(xR-xL+0.001)
    z = zB + pBA*(zA - zB)
    setPixel(int(x),int(y),z,color)
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
 frame = [0]*(width*height)
 depth = [1000]*(width*height)

 TIME = time.time()
 Views = [
  { 'center': [3,-1,math.sin(TIME*1.4)*5-5],
    'rotation': [TIME,0],
    'scale': [1.6,1,1.6] },
  { 'center': [-3,0,0],
    'rotation': [TIME,TIME/2],
    'scale': [1,1,1] }
 ]

 color = 1
 for View in Views:
  for face in faces:
   mv1 = modelview(vertex[face[0]],View)
   mv2 = modelview(vertex[face[1]],View)
   mv3 = modelview(vertex[face[2]],View)
   pt1 = project(mv1,TIME)
   pt2 = project(mv2,TIME)
   pt3 = project(mv3,TIME)
   color = face[3]
   fillTriangle(pt1,pt2,pt3,color)
   drawLine(pt1[0],pt1[1],pt1[2],pt2[0],pt2[1],pt2[2],47)
   drawLine(pt2[0],pt2[1],pt2[2],pt3[0],pt3[1],pt3[2],47)
   drawLine(pt3[0],pt3[1],pt3[2],pt1[0],pt1[1],pt1[2],47)

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
