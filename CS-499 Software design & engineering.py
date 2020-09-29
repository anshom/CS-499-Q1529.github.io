/*
 * FinalProject.cpp
 *
 *  Created on:  Sept 17, 2020
 *      Author: aurthur.nshom_snhu
 */

/*Header inclusions*/
#include <iostream> //include c++ i/o stream
#include <GL/glew.h> //includes glew header
#include <GL/freeglut.h> //includes freeglut header

//GLM math Header inclusions
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

//Soil Image loader inclusion
#include "SOIL2/SOIL2.h"

using namespace std; //uses the standard namespace

#define WINDOW_TITLE "Chair Furniture" //Macro for window Title

/*shader program macro*/
#ifndef GLSL
#define GLSL(Version, Source) "#version " #Version "\n" #Source
#endif

/*variable declarations for shader, window size initilaization, buffer and array objects*/
GLint ShaderProgram, lampShaderProgram, WindowWidth = 800, WindowHeight = 600;
GLuint VBO, VAO, LightVAO, texture;

GLfloat degrees = glm::radians(-45.0f); //converts float to degrees

GLfloat cameraSpeed = 0.5f; //Movement speed per frame

GLchar CurrentKey; //store mouse and keyboard keys

bool mouseLeftClick, mouseRightClick = false; //left and right mouse click

GLfloat lastMouseX = 400, lastMouseY = 300; //locks mouse cursor at the center of the screen
GLfloat mouseXOffset, mouseYOffset, yaw = 0.0f, pitch = 0.0f; //mouse offset,yaw, and pitch variables
GLfloat sensitivity = 0.005f; //used for mouse / camera rotaion sensitivity
bool mouseDetected = true; //initially true when mouse movement is detected

//Global vector declarations
glm::vec3 cameraPosition = glm::vec3(0.0f, 0.0f, 5.0f); //Initial camera position. placed 5 units in Z
glm::vec3 CameraUpY = glm::vec3(0.0f, 1.0f, 0.0f); //Temporary y unit vector
glm::vec3 CameraForwardZ = glm::vec3(0.0f, 0.0f, -1.0f); //Temporary z unit vector
glm::vec3 front; //Temporary z unit vector for mouse
glm::vec3 Position(0.0f, 0.0f, 0.0f);
glm::vec3 Scale(2.0f);

//Enhanced object and light color
glm::vec3 objectColor(0.6f, 0.5f, 0.75f);
glm::vec3 lightColor(1.0f, 1.0f, 1.0f);

//Light position and scale
glm::vec3 lightPosition(0.5f, 0.5f, -3.0f);
glm::vec3 lightScale(0.3f);

//camera rotation
float cameraRotation = glm::radians(-25.0f);

/*function prototype*/
void UResizeWindow(int, int);
void URenderGraphics(void);
void UCreateShader(void);
void UCreateBuffers(void);
void UGenerateTexture(void);

void UMouseMove(int x, int y);

void UKeyboard(unsigned char key, int x, int y);
void UKeyReleased(unsigned char key, int x, int y);
void UMouseClick(int button, int state, int x, int y);
void UMousePressedMove(int x, int y);

/* Vertex shader source code*/
const GLchar * VertexShaderSource = GLSL(330,
		layout (location = 0) in vec3 position; //vertex data from vertex Attrib Pointer 0
		//layout (location = 1) in vec3 color;	//color data from vertex Attrib Pointer 1
		layout (location = 1) in vec2 textureCoordinate; //texture data from VAP 1
		layout (location = 2) in vec3 normal; //VAP position 2 for normals
		//out vec3 mobileColor;	//variabel to transfer color data to the fragment shader

		out vec2 mobileTextureCoordinate;
		out vec3 Normal; //For outgoing normals to fragment shader
		out vec3 FragmentPos; //For outgoing color / pixels to fragment shader

		// Global variabels for the transform matricies
		uniform mat4 model;
		uniform mat4 view;
		uniform mat4 projection;

void main(){
	gl_Position = projection * view * model * vec4(position, 1.0f); //transform vertices to clip coordinates
	//mobileColor = color; //references incoming color data
	mobileTextureCoordinate = vec2(textureCoordinate.x, 1.0f - textureCoordinate.y); //filps the texture horizontally

	FragmentPos = vec3(model * vec4(position, 1.0f)); //Gets fragment / pixel position in world space only (exclude view and projection)

	Normal = mat3(transpose(inverse(model))) * normal; //get normal vectors in world space only and exclude normal translation properties
	}
);

/* Fragment shader program source code*/
const GLchar * FragmentShaderSource = GLSL(330,

	in vec2 mobileTextureCoordinate;
	in vec3 Normal; //For incoming normals
	in vec3 FragmentPos; //For incoming fragments
	//in vec3 mobileColor; //variable to hold incoming color data from vertex

	//out vec4 gpuColor;	//variable to pass color data to GPU
	out vec4 gpuTexture; //variable to pass color data to GPU
	//out vec4 Color;	//For outgoing cube color to the GPU
	uniform sampler2D uTexture; //Useful when working with multiple textures

	//Uniform / Global variables for object color, light color, light position, and camera/view position
	uniform vec3 objectColor;
	uniform vec3 lightColor;
	uniform vec3 lightPos;
	uniform vec3 viewPosition;

	void main(){

		/*Phong lighting model calculations to generate ambient, diffuse, and specular component*/

		//Calculate Ambient lighting
		float ambientStrength = 0.1f; //set ambient or global lighting strength
		vec3 ambient = ambientStrength * lightColor; //Generate ambient light color

		//Calculate diffuse lighting
		vec3 norm = normalize(Normal); //Normalize vectors to 1 unit
		vec3 lightDirection = normalize(lightPos - FragmentPos); //Calculate distance (Light direction) between light source and fragments/pixels on
		float impact = max(dot(norm, lightDirection), 0.0); //Calculate diffuse impact by generating dot product of normal and light
		vec3 diffuse = impact * lightColor; //Generate diffuse light color

		//Calculate specular lighting
		float specularIntensity = 0.8f; //set specular light strength
		float highlightSize = 16.0f; //set specular highlight size
		vec3 viewDir = normalize(viewPosition - FragmentPos); //Calculate view direction
		vec3 reflectDir = reflect(-lightDirection, norm); //Calcualte reflection vector

		//calculate specular component
		float specularComponent = pow(max(dot(viewDir, reflectDir), 0.0), highlightSize);
		vec3 specular = specularIntensity * specularComponent * lightColor;

		//Calculate phong result
		vec3 phong = (ambient + diffuse + specular) * objectColor;
		Color = vec4(phong, 1.0f); //send lighting results to GPU

		//gpuColor = vec4(mobileColor, 1.0);	//sends color data to the GPU for rendering
		gpuTexture = texture(uTexture, mobileTextureCoordinate); //sends texture to the GPU for rendering
	}
);

/* Lamp Shader source code*/
const GLchar * lampVertexShaderSource = GLSL(330,

		layout (location = 0) in vec3 position; //VAP position 0 for vertex position data

		layout (location = 1) in vec2 textureCoordinate; //texture data from VAP 1

		out vec2 mobileTextureCoordinate;

	//Uniform/ Global variables for the transform matrices
	uniform mat4 model;
	uniform mat4 view;
	uniform mat4 projection;

	void main()
	{
		gl_Position = projection * view * model * vec4(position, 1.0f); //Transforms vertices into clip coordinates

		mobileTextureCoordinate = vec2(textureCoordinate.x, 1.0f - textureCoordinate.y); //filps the texture horizontally
	}

);

/*Fragment Shader Source Code*/
const GLchar * lampFragmentShaderSource = GLSL(330,

		out vec4 color; //For outgoing lamp color (smaller cube) to the GPU

		in vec2 mobileTextureCoordinate;

		out vec4 gpuTexture; //variable to pass color data to GPU
		//out vec4 Color;	//For outgoing cube color to the GPU
		uniform sampler2D uTexture; //Useful when working with multiple textures


void main()
{
	//Implemented this enhancement after code review process
	gpuTexture = texture(uTexture, mobileTextureCoordinate); //sends texture to the GPU for rendering
	//color = vec4(1.0f); //set color to white (1.0f, 1.0f, 1.0f) with alpha 1.0
	}
);


//Main program
int main(int argc, char* argv[])
{
	glutInit(&argc, argv);
	glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA);
	glutInitWindowSize(WindowWidth, WindowHeight);
	glutCreateWindow(WINDOW_TITLE);

	glutReshapeFunc(UResizeWindow);

	glewExperimental = GL_TRUE;
			if (glewInit() != GLEW_OK)
			{
				std::cout <<"Failed to initialize GLEW" << std::endl;
				return -1;
			}

	UCreateShader();

	UCreateBuffers();

	UGenerateTexture();

	//Change background color after performing code review
	glClearColor(0.0f, 1.0f, 0.0f, 1.0f);	//set background color

	glutDisplayFunc(URenderGraphics);

	glutKeyboardFunc(UKeyboard); //Detects key press
	glutKeyboardUpFunc(UKeyReleased); //Detects key release
	glutMouseFunc(UMouseClick); //Detects Mouse click

	glutPassiveMotionFunc(UMouseMove); //Detects mouse movement
	glutMotionFunc(UMousePressedMove); //Detects mouse press and movement

	glutMainLoop();

	//Destroys buffer objects once used
	glDeleteVertexArrays(1, &VAO);
	glDeleteVertexArrays(1, &LightVAO);
	glDeleteBuffers(1, &VBO);

	return 0;

	}

/* Resizes the window*/
void UResizeWindow(int w, int h)
{
	WindowWidth = w;
	WindowHeight = h;
	glViewport(0, 0, WindowWidth, WindowHeight);
}

//Render Graphics
void URenderGraphics(void)
{
	//Orbits around the center
	//Get around not rendering when mouse and alt were not pressed at start
	front.x = 10.0f * cos(yaw);
	front.y = 10.0f * sin(pitch);
	front.z = sin(yaw) * cos(pitch) * 10.0f;

	glEnable(GL_DEPTH_TEST);	//Enable z-depth
	//glEnable(GL_NORMALIZE); //Automatically normalize normals
	//glShadeModel(GL_SMOOTH); //Enable smooth shading
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); //Clears the screen

	//GLint modelLoc, viewLoc, projLoc,
	GLint objectColorLoc, lightColorLoc, lightPositionLoc, viewPositionLoc;

	glm::mat4 model;
	glm::mat4 view;
	glm::mat4 projection;

	glBindVertexArray(VAO);	//Activate the vertex array object before rendering and transforming them

	/****** Use the Shader and activate the Cube Vertex Array Object for rendering and transforming******/
	glUseProgram(ShaderProgram);
	CameraForwardZ = front; //Replaces camera forward vector with radians normalized as a unit vector

	//Transform the object
	//glm::mat4 model;
	model = glm::translate(model, glm::vec3(0.0, 0.0f, 0.0f));	//place the object at the center of the viewport
	model = glm::rotate(model, 45.0f, glm::vec3(0.0, 1.0f, 0.0f));	//Rotate the objecct 45 degrees on the X
	model = glm::scale(model, glm::vec3(2.0f, 2.0f, 2.0f));	//increase the object's size by a scale of 2

	//Transform the Camera
	//glm::mat4 view;
	view = glm::lookAt(CameraForwardZ, cameraPosition, CameraUpY);

	//Transform the cube
	model = glm::translate(model, Position);
	model = glm::scale(model, Scale);

	//Transform the camera
	view = glm::translate(view, cameraPosition);
	view = glm::rotate(view, cameraRotation, glm::vec3(0.0f, 1.0f, 0.0f));

	//Creates a perspective projection
	//glm::mat4 projection;
	projection = glm::perspective(45.0f, (GLfloat)WindowWidth / (GLfloat)WindowHeight, 0.1f, 100.0f);

	//Retrieves and passes transform matrices to the shader program
	GLint modelLoc = glGetUniformLocation(ShaderProgram, "model");
	GLint viewLoc = glGetUniformLocation(ShaderProgram, "view");
	GLint projLoc = glGetUniformLocation(ShaderProgram, "projection");

	//pass matrix data to the shader program's matrix uniforms
	glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
	glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
	glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm::value_ptr(projection));

	//Reference matrix uniforms from the shader program
	objectColorLoc = glGetUniformLocation(ShaderProgram, "objectColor");
	lightColorLoc = glGetUniformLocation(ShaderProgram, "lightColor");
	lightPositionLoc = glGetUniformLocation(ShaderProgram, "lightPos");
	viewPositionLoc = glGetUniformLocation(ShaderProgram, "viewPosition");

	//Pass object,color, light, and camera data to the Shader program's corresponding uniforms
	glUniform3f(objectColorLoc, objectColor.r, objectColor.g, objectColor.b);
	glUniform3f(lightColorLoc, lightColor.r, lightColor.g, lightColor.b);
	glUniform3f(lightPositionLoc, lightPosition.x, lightPosition.y, lightPosition.z);
	glUniform3f(viewPositionLoc, cameraPosition.x, cameraPosition.y, cameraPosition.z);

	//Draws the 3D Scene
	glDrawArrays(GL_QUADS, 0, 135);

	glBindVertexArray(0);	//Deactivate the vertex Array Object
	glBindTexture(GL_TEXTURE_2D, texture);

/**** Use the Lamp shader and activate the lamp vertex array object and transforming****/
		glUseProgram(lampShaderProgram);
		glBindVertexArray(LightVAO);

		//Transform the smaller object used as a visual que for the light souce
		model = glm::translate(model, lightPosition);
		model = glm::scale(model, lightScale);

		//Reference matrix uniforms from the lamp shader program
		modelLoc = glGetUniformLocation(lampShaderProgram, "model");
		viewLoc = glGetUniformLocation(lampShaderProgram, "view");
		projLoc = glGetUniformLocation(lampShaderProgram, "projection");

		//pass matrix data to the lamp shader program's matrix uniforms
		glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
		glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
		glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm::value_ptr(projection));

		glDrawArrays(GL_QUADS, 0, 135); //Draw the primitieve/small(lamp)

		glBindVertexArray(0); //Deactive the lamp vertex Array object

		glutPostRedisplay(); //Marks the current window to be redisplayed
		glutSwapBuffers();	//Flips the back buffer with the front buffer every frame. Similar to GL Flush

}

//creates a shader program object
void UCreateShader()
{

	// vertex shader
	GLint VertexShader = glCreateShader(GL_VERTEX_SHADER);	//creates the vertex shader
	glShaderSource(VertexShader, 1, &VertexShaderSource, NULL);	//Retrieves the vertex shader source code
	glCompileShader(VertexShader);	//Compiles the vertex shader

	//fragment shader
	GLint FragmentShader = glCreateShader(GL_FRAGMENT_SHADER);	//creates the fragment shader
	glShaderSource(FragmentShader, 1, &FragmentShaderSource, NULL);	//Attaches the fragment shader to the source code
	glCompileShader(FragmentShader); 	//Compiles the fragment shader

	//shader program
	ShaderProgram = glCreateProgram();	//creates the shader program and returns an id
	glAttachShader(ShaderProgram, VertexShader);	//Attach shader program to the shader progam
	glAttachShader(ShaderProgram, FragmentShader);;	//Attach fragment shader to the shader program
	glLinkProgram(ShaderProgram);	//Link vertex and fragment shader to shader program

	//Delete the vertex and fragment shaders once linked
	glDeleteShader(VertexShader);
	glDeleteShader(FragmentShader);

	//lamp vertex shaderr
	GLint lampVertexShader = glCreateShader(GL_VERTEX_SHADER); //Creates the vertex shader
	glShaderSource(lampVertexShader, 1, &lampVertexShaderSource, NULL); //Attaches the vertex shader to the source code
	glCompileShader(lampVertexShader); //Compiles the vertex shader

	//lamp Fragment shader
	GLint lampFragmentShader = glCreateShader(GL_FRAGMENT_SHADER); //Creates the Fragment shader
	glShaderSource(lampFragmentShader, 1, &lampFragmentShaderSource, NULL); //Attaches the Fragment shader to the source code
	glCompileShader(lampFragmentShader); //Compiles the Fragment shader

	//lamp shader program
	lampShaderProgram = glCreateProgram();	//creates the shader program and returns an id
	glAttachShader(lampShaderProgram, lampVertexShader);	//Attach vertex shader to the shader progam
	glAttachShader(lampShaderProgram, lampFragmentShader);;	//Attach fragment shader to the shader program
	glLinkProgram(lampShaderProgram);	//Link vertex and fragment shader to shader program

	//Delete the lamp shaders once linked
	glDeleteShader(lampVertexShader);
	glDeleteShader(lampFragmentShader);

}

/*creates the buffer and array objects*/
void UCreateBuffers()
{
	//position and Texture data
	GLfloat vertices[] = {

			//vertex position 		//Texture       //Normals
			//Front
		  0.0f, 0.0f, 1.0f, 	0.0f, 0.0f, 1.0f,  0.0f, 0.0f, -1.0f,
		 -2.0f, -0.2f, 2.0f,    1.0f, 0.0f, 1.0f,  0.0f, 0.0f, -1.0f,
		  2.0f, -0.2f, 2.0f,	1.0f, 0.0f, 1.0f,  0.0f, 0.0f, -1.0f,
		  2.0f, 0.2f, 2.0f, 	1.0f, 0.0f, 1.0f,  0.0f, 0.0f, -1.0f,
		 -2.0f, 0.2f, 2.0f,     1.0f, 0.0f, 1.0f,  0.0f, 0.0f, -1.0f,

		 //Right
		 1.0f, 0.0f, 0.0f,    1.0f, 0.0f, 0.0f,  0.0f, 0.0f, 1.0f,
		 2.0f, -0.2f,-2.0f,   0.0f, 0.0f, 1.0f,  0.0f, 0.0f, 1.0f,
		 2.0f, 0.2f, -2.0f,   1.0f, 0.0f, 0.0f,  0.0f, 0.0f, 1.0f,
		 2.0f, 0.2f,  2.0f,   1.0f, 0.0f, 0.0f,  0.0f, 0.0f, 1.0f,
		 2.0f, -0.2f, 2.0f,   0.0f, 0.0f, 0.0f,  0.0f, 0.0f, 1.0f,

		 //Back
		  0.0f, 0.0f, -1.0f,    1.0f, 0.0f, 1.0f,  -1.0f, 0.0f, 0.0f,
		 -2.0f, -0.2f, -2.0f,  1.0f, 0.0f, 0.0f,  -1.0f, 0.0f, 0.0f,
		 -2.0f, 0.2f, -2.0f,   0.0f, 0.0f, 1.0f,  -1.0f, 0.0f, 0.0f,
		  2.0f, 0.2f, -2.0f,   1.0f, 0.0f, 1.0f,  -1.0f, 0.0f, 0.0f,
		  2.0f, -0.2f, -2.0f,  0.0f, 0.0f, 1.0f,  -1.0f, 0.0f, 0.0f,

		 //Left
		 -1.0f,  0.0f, 0.0f,   1.0f, 0.0f, 1.0f,  1.0f, 0.0f, 0.0f,
		 -2.0f, -0.2f, -2.0f,  0.0f, 0.0f, 0.0f,  1.0f, 0.0f, 0.0f,
		 -2.0f, -0.2f,  2.0f,  1.0f, 0.0f, 1.0f,  1.0f, 0.0f, 0.0f,
		 -2.0f,  0.2f,  2.0f,  0.0f, 0.0f, 0.0f,  1.0f, 0.0f, 0.0f,
		 -2.0f,  0.2f, -2.0f,  1.0f, 0.0f, 0.0f,  1.0f, 0.0f, 0.0f,

		 //Top
		  0.0f, 1.0f, 0.0f,   1.0f, 0.0f, 1.0f,  0.0f, -1.0f, 0.0f,
		  2.0f, 0.2f, 2.0f,   0.0f, 0.0f, 0.0f,  0.0f, -1.0f, 0.0f,
		 -2.0f, 0.2f, 2.0f,   1.0f, 0.0f, 1.0f,  0.0f, -1.0f, 0.0f,
		 -2.0f, 0.2f, -2.0f,  0.0f, 0.0f, 0.0f,  0.0f, -1.0f, 0.0f,
		  2.0f, 0.2f, -2.0f,  1.0f, 0.0f, 0.0f,  0.0f, -1.0f, 0.0f,
		  //Bottom
		  0.0f, -1.0f, 0.0f,   0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		  2.0f, -0.2f, 2.0f,   1.0f, 0.0f, 0.0f,  0.0f, 1.0f, 0.0f,
		  -2.0f, -0.2f, 2.0f,  0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		  -2.0f, -0.2f, -2.0f, 1.0f, 0.0f, 0.0f,  0.0f, 1.0f, 0.0f,
		  2.0f, -0.2f, -2.0f,  0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		  //table front leg
		 //front
		 0.0f, 0.0f, 1.0f, 0.0f,  0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f,-0.2f, 1.6f, 0.0f,  1.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f,-0.2f, 1.6f, 0.0f,  0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -3.0f, 1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -3.0f, 1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //back
		 0.0f,  0.0f,-1.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -0.2f, 1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -0.2f, 1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -3.0f, 1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -3.0f, 1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //right
		 1.0f,  0.0f, 0.0f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -0.2f, 1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -0.2f, 1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -3.0f, 1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -3.0f, 1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //left
		-1.0f,  0.0f, 0.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -0.2f, 1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -0.2f, 1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -3.0f, 1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -3.0f, 1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //back leg back
		 //front
		 0.0f,  0.0f, -1.0f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -0.2f, -1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -0.2f, -1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -3.0f, -1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -3.0f, -1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //back
		 0.0f,  0.0f, -1.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -0.2f, -1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -0.2f, -1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -3.0f, -1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -3.0f, -1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //right
		 1.0f,  0.0f,  0.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -0.2f, -1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -0.2f, -1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -3.0f, -1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, -3.0f, -1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //left
		 1.0f,  0.0f,  0.0f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -0.2f, -1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -0.2f, -1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -3.0f, -1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.4f, -3.0f, -1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //leg left front
		 0.0f,  0.0f, 1.0f,  0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -0.2f, 1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -0.2f, 1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -3.0f, 1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -3.0f, 1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //back
		 0.0f,  0.0f,-1.0f,  1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -0.2f, 1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -0.2f, 1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -3.0f, 1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -3.0f, 1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //right
		 1.0f,  0.0f, 0.0f,  0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -0.2f, 1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -0.2f, 1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -3.0f, 1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -3.0f, 1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //left
		 -1.0f,  0.0f, 0.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -0.2f, 1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -0.2f, 1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -3.0f, 1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -3.0f, 1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //left leg back front
		 //front
		 0.0f,  0.0f, -1.0f,  0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -0.2f, -1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -0.2f, -1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -3.0f, -1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -3.0f, -1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //back
		 0.0f,  0.0f, -1.0f,  1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -0.2f, -1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -0.2f, -1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -3.0f, -1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -3.0f, -1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //right
		  1.0f,  0.0f,  0.0f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -0.2f, -1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -0.2f, -1.2f, 0.0f, 0.0f, 0.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -3.0f, -1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.8f, -3.0f, -1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //left
		 -1.0f,  0.0f,  0.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -0.2f, -1.6f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -0.2f, -1.2f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -3.0f, -1.2f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 -1.4f, -3.0f, -1.6f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		//chair back
		 //front
		-1.0f, 0.0f, 0.0f,  0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 0.2f, -1.8f, 1.0f, 0.0f, 0.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 0.2f, -1.8f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 3.5f, -1.8f, 1.0f, 0.0f, 0.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 3.5f, -1.8f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		 //back

		 0.0f, 1.0f, 0.0f,  1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 0.2f, -2.0f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 0.2f, -2.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 3.5f, -2.0f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 3.5f, -2.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		-1.0f, 0.0f, 0.0f,  1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 0.2f, -2.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 3.5f, -2.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 3.5f, -1.8f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 0.2f, -1.8f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		-1.0f, 0.0f, 0.0f,  1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 0.2f, -2.0f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 3.5f, -2.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 3.5f, -1.8f, 0.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 0.2f, -1.8f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,

		-1.0f, 0.0f, 0.0f,  1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 3.5f, -2.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		-1.8f, 3.5f, -1.8f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 3.5f, -1.8f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,
		 1.8f, 3.5f, -2.0f, 1.0f, 0.0f, 1.0f,  0.0f, 1.0f, 0.0f,


		  };

	//Generate buffer Ids
	glGenVertexArrays(1, &VAO); //Vertex array  object vertices
	glGenBuffers(1, &VBO);

	//Activate the vertex array object before binding and setting VBOs
	glBindVertexArray(VAO);

	//Activate the VBO
	glBindBuffer(GL_ARRAY_BUFFER, VBO);
	glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW); //copy vertices to VBO

	//Set attribute pointer to 0 to hold position data
	glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(GLfloat), (GLvoid*)0);
	glEnableVertexAttribArray(0);	//Enables vertex attribute

	//Set attribute pointer 1 to hold Texture coordinates data
	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(GLfloat), (GLvoid*)(3 * sizeof(GLfloat)));
	glEnableVertexAttribArray(1);	//Enable vertex attribute

	//Set attribute pointer 2 to hold Normals coordinates data
	glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(GLfloat), (GLvoid*)(3 * sizeof(GLfloat)));
	glEnableVertexAttribArray(2);	//Enable vertex attribute

	glBindVertexArray(0);	//Deactivate the VAO which is good practice

	//Generate buffer ids for lamp (smaller)
	glGenVertexArrays(1, &LightVAO); //Vertex array object for vertex copies to serve as light source

	//Activate the Vertex Array Object before binding and setting any VBOs and vertex Attribute pointers
	glBindVertexArray(LightVAO);

	//Referencing the same VBO for its vertices
	glBindBuffer(GL_ARRAY_BUFFER,VBO);

	//Set attribute pointer to 0 to hold position data (used for the lamp)
	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(GLfloat), (GLvoid*)0);
	glEnableVertexAttribArray(1);	//Enables vertex attribute
	glBindVertexArray(1);

	//Set attribute pointer 1 to hold Texture coordinates data(Lamp)
	glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 9 * sizeof(GLfloat), (GLvoid*)(3 * sizeof(GLfloat)));
	glEnableVertexAttribArray(1);	//Enable vertex attribute


}

//Generate and load the texture
void UGenerateTexture(){

	glGenTextures(1, &texture);
	glBindTexture(GL_TEXTURE_2D, texture);

	int width, height;

	unsigned char* image = SOIL_load_image("snhu.jpg", &width, &height, 0, SOIL_LOAD_RGB); //Loads texture file

	glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image);
	glGenerateMipmap(GL_TEXTURE_2D);
	SOIL_free_image_data(image);
	glBindTexture(GL_TEXTURE_2D, 0); //Unbind the texture

}

/*Implements the UMouseMove function*/
void UMouseMove(int x, int y)
{
	//Immediately replaces center locked coordinates with new mouse coordinates
	if(mouseDetected)
		{
			lastMouseX = x;
			lastMouseY = y;
			mouseDetected = false;
		}

	//Gets the direction the mouse was moved in x and y
	mouseXOffset = x - lastMouseX;
	mouseYOffset = lastMouseY - y; //Inverted Y

	//Updates with new mouse coordinates
	lastMouseX = x;
	lastMouseY = y;

	//Applies sensitivity to mouse direction
	mouseXOffset *= sensitivity;
	mouseYOffset *= sensitivity;

	//Accumulates the yaw and pitch variables
	yaw += mouseXOffset;
	pitch += mouseYOffset;
}

/*Implements the UKeyboard function*/
void UKeyboard(unsigned char key, GLint x, GLint y)
{
	switch(key){
	case 'w':
		break;
	default:
		cout<<"Press a Key!"<<endl;
	}
}

/*Implements the UKeyReleased function*/
void UKeyReleased(unsigned char key, GLint x, GLint y)
{
	switch(key){
	case 'w':
		break;
	default:
			cout<<"Press a Key!"<<endl;
	}

}

//Implement the UMouseClick Function
void UMouseClick(int button, int state, int x, int y)
{
	if ((button == GLUT_LEFT_BUTTON) && (state == GLUT_DOWN)){
			mouseLeftClick = true;
	}

	if ((button == GLUT_LEFT_BUTTON) && (state == GLUT_UP)){
				mouseLeftClick = false;

	}

	if ((button == GLUT_RIGHT_BUTTON) && (state == GLUT_DOWN)){
				mouseRightClick = true;
	}

	if ((button == GLUT_RIGHT_BUTTON) && (state == GLUT_UP)){
				mouseRightClick = false;
				}
}

//Implements the UMousePrssedMove function
void UMousePressedMove(int x, int y)
{
	//immediately replaces center locked coordinates with new mouse coordinates
	if (mouseDetected)
	{
		lastMouseX = x;
		lastMouseY = y;
		mouseDetected = false;
	}

	//Gets the direction the mouse was moved in x and y
	mouseXOffset = x - lastMouseX;
	mouseYOffset = lastMouseY - y;

	//Updates with new mouse coordinates
	lastMouseX = x;
	lastMouseY = y;

	//Applies sensitivity to mouse direction
	mouseXOffset *= sensitivity;
	mouseYOffset *= sensitivity;

	int mod = glutGetModifiers(); //Get the current modifiers and check if alt is active
	if (mod == GLUT_ACTIVE_ALT)
	{
		if (mouseLeftClick)
		{
			//Accumulates the yaw and pitch variables
			yaw += mouseXOffset;
			pitch += mouseYOffset;
		}
		else
			if (mouseRightClick == true)
			{
				cameraPosition += -mouseYOffset * cameraSpeed * CameraForwardZ; //Multiply by mouseYOffset to  zoom in and out

			}
	}

}














