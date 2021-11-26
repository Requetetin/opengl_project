import pygame
import numpy
from obj import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import glm

pygame.init()
screen = pygame.display.set_mode((1200, 720), pygame.OPENGL | pygame.DOUBLEBUF)
glClearColor(0.1, 0.2, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
clock = pygame.time.Clock()

#Cambiar esta variable para cambiar el shader
usando = 1

vertex_shader = """
#version 460

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 ccolor;

uniform mat4 theMatrix;

out vec3 mycolor;

void main() 
{
  gl_Position = theMatrix * vec4(position.x, position.y, position.z, 1);
  mycolor = ccolor;
}
"""

fragment_shader = """
#version 460
layout(location = 0) out vec4 fragColor;

uniform float r;
uniform float g;
uniform float b;
in vec3 mycolor;

void main()
{
  fragColor = vec4(r, g, b, 1.0f);
}
"""

fragment_shader2 = """
#version 460
layout(location = 0) out vec4 fragColor;

uniform float transp;
in vec3 mycolor;

void main()
{
  fragColor = vec4(mycolor.xyz, transp);
}
"""

fragment_shader3 = """
#version 460
layout(location = 0) out vec4 fragColor;

uniform float red;
uniform float green;
uniform float blue;
in vec3 mycolor;

void main()
{
  fragColor = vec4(red, green, blue, 1.0);
}
"""

cvs = compileShader(vertex_shader, GL_VERTEX_SHADER)
if usando == 1:
  cfs = compileShader(fragment_shader, GL_FRAGMENT_SHADER)
if usando == 2:
  cfs = compileShader(fragment_shader2, GL_FRAGMENT_SHADER)
if usando == 3:
  cfs = compileShader(fragment_shader3, GL_FRAGMENT_SHADER)

shader = compileProgram(cvs, cfs)

mesh = Obj('./among.obj')

len1 = len(mesh.vertices)
len2 = len(mesh.normals)
vertex_data = numpy.hstack((
  numpy.array(mesh.vertices[0:min(len1, len2)], dtype=numpy.float32),
  numpy.array(mesh.normals[0:min(len1, len2)], dtype=numpy.float32),
)).flatten()

index_data = numpy.array([[vertex[0] for vertex in face] for face in mesh.faces], dtype=numpy.uint32).flatten()

vertex_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

vertex_array_object = glGenVertexArrays(1)
glBindVertexArray(vertex_array_object)
glVertexAttribPointer(
  0, # location
  3, # size
  GL_FLOAT, # tipo
  GL_FALSE, # normalizados
  4 * 6, # stride
  ctypes.c_void_p(0)
)
glEnableVertexAttribArray(0)

element_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, element_buffer_object)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

glVertexAttribPointer(
  1, # location
  3, # size
  GL_FLOAT, # tipo
  GL_FALSE, # normalizados
  4 * 6, # stride
  ctypes.c_void_p(4 * 3)
)
glEnableVertexAttribArray(1)

glUseProgram(shader)


from math import sin

def render(angle, zoom, cameray):
  i = glm.mat4(1)

  translate = glm.translate(i, glm.vec3(0, -5, 0))
  rotate = glm.rotate(i, glm.radians(angle), glm.vec3(0, 1, 0))
  scale = glm.scale(i, glm.vec3(0.25, 0.25, 0.25))

  model = translate * rotate * scale
  view = glm.lookAt(glm.vec3(0, cameray, zoom), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
  projection = glm.perspective(glm.radians(45), 1200/720, 0.1, 1000.0)

  theMatrix = projection * view * model

  glUniformMatrix4fv(
    glGetUniformLocation(shader, 'theMatrix'),
    1,
    GL_FALSE,
    glm.value_ptr(theMatrix)
  )

glViewport(0, 0, 1200, 720)


print('\nPara cambiar el shader, ir a la linea 17. Seleccionar valor entre 1 y 3')

print('\n\nScroll wheel for zoom in/out')
print('Left and right arrow keys for object rotation')
print('Up and down arrow keys for camera movement\n\n')

if usando == 3:
  print('\nUse w y s para cambiar el rojo \na y d para cambiar el verde\nq y e para cambiar azul')

angle = 0
zoom = 20
cameray = 0

state = 0
r = 255
g = 0
b = 0

transparency = 0

rojo = 0
verde = 0
azul = 0

running = True
while running:
  glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

  render(angle, zoom, cameray)

  glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)

  pygame.display.flip()
  clock.tick(15)

  if usando == 1:
    if state == 0:
      g += 1
      if g == 255:
        state = 1

    if state == 1:
      r -= 1
      if r == 0:
        state = 2

    if state == 2:
      b += 1
      if b == 255:
        state = 3

    if state == 3:
      g -= 1
      if g == 0:
        state = 4

    if state == 4:
      r += 1
      if r == 255:
        state = 5

    if state == 5:
      b -= 1
      if b == 0:
        state = 0

    red = r / 255
    green = g / 255
    blue = b / 255

    glUniform1f(
      glGetUniformLocation(shader, 'r'),
      red
    )
    glUniform1f(
      glGetUniformLocation(shader, 'g'),
      green
    )
    glUniform1f(
      glGetUniformLocation(shader, 'b'),
      blue
    )
  if usando == 2:
    transparency += 0.5
    glUniform1f(
      glGetUniformLocation(shader, 'transp'),
      ((sin(transparency) + 1) / 2)
    )
    pygame.time.wait(200)
  if usando == 3:
    glUniform1f(
      glGetUniformLocation(shader, 'red'),
      rojo%255 / 255
    )
    glUniform1f(
      glGetUniformLocation(shader, 'green'),
      verde%255 / 255
    )
    glUniform1f(
      glGetUniformLocation(shader, 'blue'),
      azul%255 / 255
    )

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RIGHT:
        angle += 1
      if event.key == pygame.K_LEFT:
        angle -= 1
      if event.key == pygame.K_UP:
        cameray += 1
      if event.key == pygame.K_DOWN:
        cameray -= 1
      if event.key == pygame.K_w:
        rojo += 1
      if event.key == pygame.K_s:
        rojo -= 1
      if event.key == pygame.K_a:
        verde -=1
      if event.key == pygame.K_d:
        verde +=1
      if event.key == pygame.K_q:
        azul -= 1
      if event.key == pygame.K_e:
        azul += 1
    if event.type == pygame.MOUSEWHEEL:
      zoom -= event.y
