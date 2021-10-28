/////////////////////////////////////////////////////////////////
//
//	helloServer.cpp
//
//	Adapted from Douglas Comer's "Internetworking with TCP/IP"
//	by Jeff Ondich and Lauren Jantz, summer 1995.
//
//	Rewritten in C++, Jeff Ondich, January 2000.
//
//	This program is an iterative server for a tiny "hello
//	world" sort of protocol.  Once a TCP connection request
//	arrives, this server accepts the connection, sends
//	a null-terminated message string to the client, and
//	then closes the connection.
//
//	See helloClient.cpp for more details.
//
/////////////////////////////////////////////////////////////////

//#include	<iostream>
//#include	<string>
#include	<stdio.h>
#include	<stdlib.h>

#include	<errno.h>
#include	<string.h>
#include	<unistd.h>
#include	<sys/types.h>
#include	<sys/socket.h>
#include	<netinet/in.h>
#include	<netdb.h>

#include	"tcpUtilities.h"

//////////////////////////////////////////////////
// Prototypes of functions in this file.
//////////////////////////////////////////////////

void ParseCommandLine( int argc, char **argv, int *port, char *message );
void LogConnection( int sock, const char *serverName );
void ProcessRequest( int sock, const char *message );


int main( int argc, char **argv )
{
	/////////////////////////////////////////////////
	// Process the command line arguments to
	// determine the desired port and hello message.
	/////////////////////////////////////////////////

	int 	port;
	char	message[4096];
	ParseCommandLine( argc, argv, &port, message );


	/////////////////////////////////////////////////
	// Start listening at the specified port.
	/////////////////////////////////////////////////

	int mainSock = PrepareToAcceptConnections( port );

	fprintf(stderr, "%s is ready to serve at port %d.\n", argv[0], port);


	/////////////////////////////////////////////////
	// Accept and process connections until
	// the world ends.
	/////////////////////////////////////////////////

	while( 1 )
	{
		/////////////////////////////////////////////////
		// Answer the phone.  Note that Accept()
		// makes a duplicate of the original socket
		// so that, if you wished, you could have
		// the server listen for more connection
		// requests while at the same time processing
		// the current request.  See
		// helloServerConcurrent.cpp for how to
		// do so.
		/////////////////////////////////////////////////

		int tmpSock = Accept( mainSock );
		if( tmpSock < 0 )
		{
			fprintf(stderr, "%s: accept failed: %s\n", argv[0], strerror(errno));
			exit(1);
		}



		/////////////////////////////////////////////////
		// Process the request.
		/////////////////////////////////////////////////

		LogConnection( tmpSock, argv[0] );
		ProcessRequest( tmpSock, message );




		/////////////////////////////////////////////////
		// Close the connection.
		/////////////////////////////////////////////////

		close( tmpSock );
	}

	return( 0 );
}


//////////////////////////////////////////////////
// For complicated command line syntax, this
// parsing can get pretty hairy, so I moved
// it out of main() with this function.  A
// lot of the standard UNIX commands, however,
// leave the command line parsing in main().
//////////////////////////////////////////////////

void ParseCommandLine( int argc, char **argv, int *port, char *message )
{
	if( argc != 3 )
	{
		fprintf(stderr, "Usage: %s PORT MESSAGE\nFor example: %s 1234 \"Hi there, client.\"\n", argv[0], argv[0]);
		exit(1);
	}

	*port = atoi( argv[1] );
	strcpy(message, argv[2]);
}


//////////////////////////////////////////////////
// Log connection records information about
// the current connection request.  It could,
// of course, be more sophisticated than
// printing a message to standard error, but
// it's not.
//////////////////////////////////////////////////

void LogConnection( int sock, const char *serverName )
{
	char name[100];
	GetPeerHostName( sock, name, 100 );
	fprintf(stderr, "%s: processed request from %s\n", serverName, name);
}


//////////////////////////////////////////////////
// ProcessRequest implements the protocol.
// Since this server's protocol is pretty
// darned trivial, there's not much here.
//////////////////////////////////////////////////

void ProcessRequest( int sock, const char *message )
{
	/////////////////////////////////////////////////
	// Send the message.  Note that writing to
	// a socket is simpler than reading from one,
	// since you can write everything at once,
	// but reading depends on when the pieces
	// of the incoming message arrive from across
	// the network.
	/////////////////////////////////////////////////

	write( sock, message, strlen(message)+1 );
}

