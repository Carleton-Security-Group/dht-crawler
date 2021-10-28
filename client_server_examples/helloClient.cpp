///////////////////////////////////////////////////////////////////
//
//	helloClient.cpp
//
//	Adapted from Douglas Comer's "Internetworking with TCP/IP"
//	by Jeff Ondich and Lauren Jantz, summer 1995.
//
//	Rewritten in C++, Jeff Ondich, January 2000.
//	Command line parsing added.
//
//	This client is half of a sort of "hello world"
//	client/server pair.  The client makes a connection
//	to the server and port specified on the command line,
//	and the server sends back a snotty null-terminated
//	character string.  The client prints this message to
//	standard output on the client machine.
//
//	Note that the protocol is exceedingly simple:
//
//		1. Client initiates connection.
//		2. Server sends message, null-terminated.
//		3. Server closes connection.
//
//	In particular, the client never sends any actual
//	text to the server.  If you want your client to
//	talk to the server, you'll need to design a more
//	complicated protocol, and the client will use
//	write() to send data to the server.
//
///////////////////////////////////////////////////////////////////

#include	<iostream>
#include	<stdlib.h>
#include	<errno.h>
#include	<unistd.h>
#include	<string.h>
#include	<sys/types.h>
#include	<sys/socket.h>
#include	<netinet/in.h>

#include	"tcpUtilities.h"

int main( int argc, char **argv )
{
	//////////////////////////////////////////////////
	// Parse the command line to determine the
	// host name and port number.
	//////////////////////////////////////////////////
	
	if( argc != 3 )
	{
		cerr << "Usage:  " << argv[0] << " hostname port" << endl;
		exit(1);
	}

	int port = atoi( argv[2] );
	char *hostName = argv[1];


	//////////////////////////////////////////////////
	// Connect to the server.
	//////////////////////////////////////////////////

	int sock = MakeConnection( hostName, port );
	if( sock < 0 )
	{
		cerr << "Unable to connect to server at "
			<< hostName << ":" << port << endl;
		exit(1);
	}
			

	
	//////////////////////////////////////////////////
	// Connection made, we now read one byte at
	// a time until '\0' or the end of the stream,
	// sending each byte to standard output.
	//////////////////////////////////////////////////

	char		c;

	int i = ReadFromSocket( sock, &c, 1 );
	while( i > 0  &&  c != '\0' )
	{
		cout.put( c );
		i = ReadFromSocket( sock, &c, 1 );
	}

	cout << endl;

	if( i < 0 )
	{
		cerr << "Socket read failed: " << strerror(errno) << endl;
		exit(1);
	}

	

	//////////////////////////////////////////////////
	// When all communication is done, clean up and quit.
	//////////////////////////////////////////////////

	close( sock );

	return( 0 );
}
