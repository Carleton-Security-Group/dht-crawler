/////////////////////////////////////////////////////////////////
//
//	helloServerConcurrent.cpp
//
//	Adapted from Douglas Comer's "Internetworking with TCP/IP"
//	by Jeff Ondich and Lauren Jantz, summer 1995.
//
//	Rewritten in C++, Jeff Ondich, January 2000.
//
//	This program is a concurrent server for a tiny "hello
//	world" sort of protocol.  Once a TCP connection request
//	arrives, this server accepts the connection and creates a
//	child process to respond to the request.  The child sends
//	a null-terminated message string to the client, and
//	then closes the connection.
//
//	See helloClient.cpp for more details.
//
/////////////////////////////////////////////////////////////////

#include	<iostream>
#include	<string>

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

void ParseCommandLine( int argc, char **argv, int& port, string& message );
void LogConnection( int sock, const char *serverName );
void ProcessRequest( int sock, const string& message );


int main( int argc, char **argv )
{
	/////////////////////////////////////////////////
	// Process the command line arguments to
	// determine the desired port and hello message.
	/////////////////////////////////////////////////

	int 	port;
	string	message;
	ParseCommandLine( argc, argv, port, message );


	/////////////////////////////////////////////////
	// Start listening at the specified port.
	/////////////////////////////////////////////////
	
	int mainSock = PrepareToAcceptConnections( port );

	cerr << argv[0] << " is ready to serve at port "
		<< port << "." << endl;
	

	/////////////////////////////////////////////////
	// Accept and process connections until
	// the world ends.
	/////////////////////////////////////////////////
	
	while( 1 )
	{
		/////////////////////////////////////////////////
		// Answer the phone.  Accept() makes a
		// duplicate of the original socket.  After
		// the parent process creates a child process,
		// the child has no use for the original socket
		// (which is being used to listen for connection
		// requests), and the parent has no use for the
		// new socket, which will be used by the child
		// to process the connection request.
		/////////////////////////////////////////////////

		int tmpSock = Accept( mainSock );
		if( tmpSock < 0 )
		{
			cerr << argv[0] << ": accept failed: " << strerror(errno) << endl;
			exit(1);
		}


		/////////////////////////////////////////////////
		// Create a child process to process the
		// request so the parent can go on listening
		// for new requests.
		/////////////////////////////////////////////////

		if( fork() != 0 )
		{
			/////////////////////////////////////////////////
			// The parent, which executes this code, just
			// closes its connection to the remote host
			// and goes back to listening by calling accept()
			// at the top of the loop.
			/////////////////////////////////////////////////

			close( tmpSock );
		}

		else
		{
			/////////////////////////////////////////////////
			// The child process doesn't need to listen
			// for new connection requests, so it closes
			// its listening connection (mainSock).  Then
			// the child handles the one request it was
			// created to handle, closes its connection
			// to the remote host, and dies.
			/////////////////////////////////////////////////

			close( mainSock );
			LogConnection( tmpSock, argv[0] );
			ProcessRequest( tmpSock, message );
			close( tmpSock );
			exit( 0 );
		}
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

void ParseCommandLine( int argc, char **argv, int& port, string& message )
{
	if( argc != 3 )
	{
		cerr << "Usage: " << argv[0] << " port message" << endl
			<< "For example: " << argv[0]
			<< " 1234 \"Hi there, client.\"" << endl;
		
		exit(1);
	}

	port = atoi( argv[1] );
	message = argv[2];
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
	cerr << serverName << ": processed request from " << name << endl;
}


//////////////////////////////////////////////////
// ProcessRequest implements the protocol.
// Since this server's protocol is pretty
// darned trivial, there's not much here.
//////////////////////////////////////////////////

void ProcessRequest( int sock, const string& message )
{
	/////////////////////////////////////////////////
	// Send the message.  Note that writing to
	// a socket is simpler than reading from one,
	// since you can write everything at once,
	// but reading depends on when the pieces
	// of the incoming message arrive from across
	// the network.
	/////////////////////////////////////////////////
	
	write( sock, message.c_str(), message.length()+1 );
}

