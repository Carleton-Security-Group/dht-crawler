///////////////////////////////////////////////////////////////
//
//	tcpUtilities.cpp
//
//	Adapted in C from Douglas Comer's "Internetworking
//		with TCP/IP" by Jeff Ondich and Lauren Jantz,
//		summer 1995.
//
//	Rewritten in C++, Jeff Ondich, January 2000.
//
//	These are utility functions that are intended to make
//	very simple TCP-based client/server programs relatively
//	easy to write.
//
//	The functions here are used by the
//	example client (helloClient.cpp) and servers
//	(helloServer.cpp and helloConcurrent.cpp).
//
///////////////////////////////////////////////////////////////

#include	<iostream>
#include	<stdlib.h>
#include	<sys/types.h>
#include	<sys/socket.h>
#include	<netinet/in.h>
#include	<arpa/inet.h>
#include	<unistd.h>
#include	<netdb.h>
#include	<errno.h>
#include	<string.h>

#include	"tcpUtilities.h"



//////////////////////////////////////////////////////
//
//	MakeConnection tries to make a TCP connection
//	to the given host and given port.  The return
//	value is either -1 if the connection failed,
//	or the socket number corresponding to the
//	connection if it succeeded.  The hostName
//	can be either a domain name, like www.moose.com,
//	or a dotted-decimal IP address, like
//	123.123.123.321 .
//
//////////////////////////////////////////////////////

int MakeConnection( const char *hostName, int port )
{
	////////////////////////////////////////////////////
	// Initialize sockaddr_in struct.  Shortly, this
	// struct will receive the address of the remote
	// host.
	////////////////////////////////////////////////////

	struct sockaddr_in		remoteAddress;

	bzero( (char *)(&remoteAddress), sizeof(remoteAddress) );
	remoteAddress.sin_family = AF_INET;
	remoteAddress.sin_port = htons( (u_short)port );


	////////////////////////////////////////////////////
	// Get the destination IP address using the host
	// name, which may be something like
	// "blum.mathcs.carleton.edu", or a dotted-decimal
	// IP address string like "137.22.4.10".  The
	// resulting address is then stored in 
	// remoteAddress.sin_addr.
	////////////////////////////////////////////////////

	struct hostent *hostInfo = gethostbyname( hostName );

  	if( hostInfo )
		bcopy( hostInfo->h_addr, (char *)(&remoteAddress.sin_addr), hostInfo->h_length );

	else
	{
		////////////////////////////////////////////////////
		// The string held in hostName didn't work out as
		// a domain name, so now we'll try it as a
		// dotted-decimal IP address.
		////////////////////////////////////////////////////

		remoteAddress.sin_addr.s_addr = inet_addr( hostName );
		if( remoteAddress.sin_addr.s_addr == INADDR_NONE )
			return( -1 );
	}


	////////////////////////////////////////////////////
	//	Ask the OS for a socket to use in connecting
	//	to the remote host.
	////////////////////////////////////////////////////
  
	int sock = socket( PF_INET, SOCK_STREAM, 0 );
	if( sock < 0 )
		return( -1 );


	////////////////////////////////////////////////////
	// Connect the socket to destination address/port.
	////////////////////////////////////////////////////
  
	if( connect( sock, (struct sockaddr *)&remoteAddress, sizeof(remoteAddress) ) < 0 )
		return( -1 );
	

	////////////////////////////////////////////////////
	// The connection is good.  Return the socket.
	////////////////////////////////////////////////////

	return( sock );
}


//////////////////////////////////////////////////////
//
//	PrepareToAcceptConnections allocates and initializes a
//	socket that will act as the local endpoint of
//	incoming TCP connections.  The bind() and listen()  
//	calls, if successful, lay claim to the given
//	port so that this process will receive
//	requests for connection to the port.
//
//	This function assumes a default value for the
//	maximum length of the queue of incoming 
//	connection requests.  It also assumes 
//
//	Modified from pp. 117-118, Comer
//	"Internetworking with TCP/IP, Vol. III."
//
//////////////////////////////////////////////////////

int PrepareToAcceptConnections( int port )
{

	////////////////////////////////////////////////////
	// Allocate a socket
	////////////////////////////////////////////////////

	int sock = socket( PF_INET, SOCK_STREAM, 0 );
	if( sock < 0 )
	{
		cerr << "Can't create socket: " << strerror(errno) << endl;
		exit(1);
	}


	////////////////////////////////////////////////////
	// Initialize the socket.  This involves setting
	// up a sockaddr_in struct with info including
	// the desired port number, and then calling bind
	// to associate the socket with the port number.
	////////////////////////////////////////////////////

	struct sockaddr_in	addr;

	bzero( (char *)(&addr), sizeof(addr) );
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = INADDR_ANY;
	addr.sin_port = (u_short)htons( port );

  
	if( bind( sock, (struct sockaddr *)(&addr), sizeof(addr) ) < 0 )
	{
		cerr << "Can't bind to port " << port << ": "
			<< strerror(errno) << endl;
		exit(1);
	}


	////////////////////////////////////////////////////
	// Lay claim to the port, and prepare to call
	// accept().
	////////////////////////////////////////////////////

	if( listen( sock, DEFAULT_QUEUE_LENGTH ) < 0 )
	{
		cerr << "Can't listen on port " << port << ": "
			<< strerror(errno) << endl;
		exit(1);
	}


	////////////////////////////////////////////////////
	//	The socket is ready.  Caller may call accept().
	////////////////////////////////////////////////////
  
	return( sock );
}


//////////////////////////////////////////////////////
// Accept provides a simplified interface to 
// the accept() system call.  This is for very
// simple servers that just need to get the new
// socket's descriptor, not the accompanying
// address information that accept() returns.
//////////////////////////////////////////////////////

int Accept( int sock )
{
	struct sockaddr_in	peerAddr;
	socklen_t			addrLength = sizeof(peerAddr);
	return( accept( sock, (struct sockaddr *)&peerAddr, &addrLength ) );
}


//////////////////////////////////////////////////////
//
//	ReadFromSocket is just a fancy way to call 
//	read() over and over until a desired number
//	of characters arrive.  Since we're reading
//	from a network connection, the bytes may
//	arrive in unpredictable numbers, so read()
//	returns not when it has as many bytes as
//	requested, but simply when there are any
//	bytes to return at all.  That way, a well
//	designed program could process whatever bytes
//	it has received while waiting for more
//	(witness, for example, the gradual composition
//	of a web page in a well designed browser).
//
//	ReadFromSocket allows you to wait until
//	all your bytes have arrived.  One could
//	easily write a similar function to wait
//	until a particular byte value or combination
//	of values arrives.
//
//////////////////////////////////////////////////////

int ReadFromSocket( int sock, char *where, int bytesToRead )
{
	int		n, bytesToGo;

	bytesToGo = bytesToRead;
	while( bytesToGo > 0 )
	{
		n = read( sock, where, bytesToGo );
		if( n < 0 )
			return( n );  // error: caller should handle it
		if( n == 0 )	// EOF
			return( bytesToRead - bytesToGo );
		
		bytesToGo = bytesToGo - n;
		where = where + n;
	}
	return( bytesToRead - bytesToGo );
}


//////////////////////////////////////////////////////
//
//	GetPeerHostName returns the domain name of
//	the machine on the other end of the TCP
//	connection specified by sock.  If no name is
//	found, an empty string is returned.
//
//////////////////////////////////////////////////////

void GetPeerHostName( int sock, char *name, int nameArrayLimit )
{
	name[0] = '\0';

	struct sockaddr_in	peer;
	socklen_t			pSize = sizeof(peer);
	
	if( !getpeername( sock, (struct sockaddr *)&peer, &pSize ) )
	{
		int iSize = sizeof(struct in_addr);
		struct hostent *hostInfo;
		hostInfo = gethostbyaddr( (char *)(&peer.sin_addr), iSize, AF_INET );
		if( hostInfo )
		{
			strncpy( name, hostInfo->h_name, nameArrayLimit );
			name[nameArrayLimit-1] = '\0';
		}
	}
}

